import io
import json
import os
import stat
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import generate_cv as gc

MASTER = json.loads((gc.PROJECT_ROOT / "data" / "cv_master.json").read_text(encoding="utf-8"))


class EscapeLatexTests(unittest.TestCase):
    def test_escapes_special_characters(self):
        self.assertEqual(gc.escape_latex("100% & 20$ a_b"), r"100\% \& 20\$ a\_b")

    def test_escapes_backslash_without_double_escaping(self):
        self.assertEqual(gc.escape_latex(r"C:\Users"), r"C:\textbackslash{}Users")

    def test_escapes_braces_tilde_and_caret(self):
        self.assertEqual(gc.escape_latex("{a} ~b ^c"), r"\{a\} \textasciitilde{}b \textasciicircum{}c")

    def test_markdown_bold_becomes_textbf(self):
        self.assertEqual(gc.escape_latex("**Docker** & Nginx"), r"\textbf{Docker} \& Nginx")

    def test_bold_content_is_also_escaped(self):
        self.assertEqual(gc.escape_latex("**a_b**"), r"\textbf{a\_b}")

    def test_bullet_dot_becomes_latex_command(self):
        self.assertIn(r"\textperiodcentered{}", gc.escape_latex("a · b"))

    def test_empty_input(self):
        self.assertEqual(gc.escape_latex(""), "")

    def test_ff_is_split_for_ats_text_extraction(self):
        # XeTeX would emit the ff ligature glyph (U+FB00); keep the two letters separate.
        self.assertEqual(gc.escape_latex("Pack Office"), r"Pack Of\hspace{0pt}fice")

    def test_split_does_not_escape_the_glue(self):
        self.assertEqual(gc.escape_latex("offline **difficile**"),
                         r"of\hspace{0pt}fline \textbf{dif\hspace{0pt}ficile}")


class LanguageFallbackTests(unittest.TestCase):
    def test_requested_language_is_used(self):
        content = {"fr": {"title": "T"}, "en": {"title": "T"}}
        self.assertIs(gc.get_language_section(content, "en", "x"), content["en"])

    def test_fallback_to_french_is_warned(self):
        content = {"fr": {"title": "T"}}
        errors = io.StringIO()
        with redirect_stderr(errors):
            self.assertIs(gc.get_language_section(content, "en", "experience 'exp1'"), content["fr"])
        self.assertIn("experience 'exp1'", errors.getvalue())

    def test_flat_content_is_returned_unchanged(self):
        content = {"title": "T"}
        self.assertIs(gc.get_language_section(content, "en", "x"), content)


class DocumentBuildTests(unittest.TestCase):
    def test_french_track_renders_all_sections(self):
        doc = gc.build_latex_document(MASTER, "fullstack", "fr")
        for label in gc.SECTION_TITLES["fr"].values():
            self.assertIn(label, doc)

    def test_english_track_renders_english_labels(self):
        doc = gc.build_latex_document(MASTER, "it_support", "en")
        self.assertIn("Technical Skills", doc)
        self.assertNotIn("Compétences Techniques", doc)

    def test_unknown_track_fails_clearly(self):
        with self.assertRaises(SystemExit) as ctx:
            gc.build_latex_document(MASTER, "does_not_exist", "fr")
        self.assertIn("does_not_exist", str(ctx.exception))

    def test_project_section_is_rendered(self):
        doc = gc.build_latex_document(MASTER, "fullstack", "fr")
        first_project = MASTER["projects"][0]
        self.assertIn("\\resumeProjectHeading", doc)
        self.assertIn(first_project["fr"]["title"], doc)


class NamingTests(unittest.TestCase):
    def test_every_track_has_a_filename_label(self):
        self.assertEqual(set(gc.TRACK_LABELS), {"it_support", "fullstack", "tailored"})


class RecencyOrderTests(unittest.TestCase):
    def exp(self, exp_id, fr_dates, en_dates=None):
        block = {"dates": fr_dates}
        record = {"id": exp_id, "fr": block}
        if en_dates:
            record["en"] = {"dates": en_dates}
        return record

    def test_french_and_english_month_names_are_parsed(self):
        self.assertEqual(gc.experience_start_key(self.exp("a", "Fév 2025 -- Juin 2025"), "fr"), (2025, 2))
        self.assertEqual(gc.experience_start_key(self.exp("a", "", "May 2026 -- September 2026"), "fr"), (2026, 5))

    def test_newest_experience_comes_first(self):
        exps = [self.exp("old", "Juil 2024 -- Août 2024"),
                self.exp("current", "Nov 2025 -- Présent"),
                self.exp("recent", "Mai 2026 -- Septembre 2026")]
        self.assertEqual([e["id"] for e in gc.sort_by_recency(exps, "fr")],
                         ["recent", "current", "old"])

    def test_unparseable_date_keeps_the_authored_order(self):
        exps = [self.exp("a", "à préciser"), self.exp("b", "Mai 2026 -- Septembre 2026")]
        self.assertIs(gc.sort_by_recency(exps, "fr"), exps)



class EngineResolutionTests(unittest.TestCase):
    def make_binary(self, directory: Path, name: str, magic: bytes = b"\x7fELF") -> Path:
        path = directory / name
        path.write_bytes(magic)
        path.chmod(path.stat().st_mode | stat.S_IEXEC)
        return path

    def test_windows_binary_is_rejected_on_unix(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = self.make_binary(Path(tmp), "tectonic", b"MZ\x90\x00")
            if sys.platform == "win32":
                self.skipTest("platform check only applies off Windows")
            self.assertFalse(gc.is_runnable(exe))

    def test_explicit_override_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = self.make_binary(Path(tmp), "xelatex")
            self.assertEqual(gc.resolve_tex_engine(str(exe)), exe)


class PathResolutionTests(unittest.TestCase):
    def test_repo_relative_path_resolves_from_project_root(self):
        cwd = Path.cwd()
        os.chdir(Path(tempfile.gettempdir()))
        try:
            self.assertEqual(gc.resolve_project_path("data/cv_master.json"), gc.PROJECT_ROOT / "data" / "cv_master.json")
        finally:
            os.chdir(cwd)

    def test_missing_path_is_returned_untouched(self):
        self.assertEqual(gc.resolve_project_path("nope.json"), Path("nope.json"))


class OverrideTests(unittest.TestCase):
    def tailored(self, **kwargs):
        lang = kwargs.pop("lang", "fr")
        data = json.loads(json.dumps(MASTER))
        warnings = gc.apply_overrides(data, "it_support", lang, **kwargs)
        return gc.build_latex_document(data, "it_support", lang), warnings

    def test_subtitle_and_summary_reach_the_document(self):
        tex, warnings = self.tailored(subtitle="Technicien Reseaux N1", summary="Resume cible.")
        self.assertEqual(warnings, [])
        self.assertIn("Technicien Reseaux N1", tex)
        self.assertIn("Resume cible.", tex)

    def test_experience_ids_select_blocks_and_recency_orders_them(self):
        tex, _ = self.tailored(experience_ids=["exp_gct", "exp_ortho"])
        self.assertLess(tex.index("Orthodontie"), tex.index("Groupe Chimique"))

    def test_unknown_ids_are_warned_and_skipped(self):
        tex, warnings = self.tailored(experience_ids=["exp_gct", "exp_ghost"], project_ids=["proj_nope"])
        self.assertTrue(any("exp_ghost" in w for w in warnings))
        self.assertTrue(any("proj_nope" in w for w in warnings))
        self.assertNotIn("exp_ghost", tex)

    def test_override_falls_back_to_the_french_block(self):
        data = {"profiles": {"only_fr": {"fr": {"subtitle": "old", "summary": "old"}}}}
        gc.apply_overrides(data, "only_fr", "en", subtitle="Fallback Subtitle")
        self.assertEqual(data["profiles"]["only_fr"]["fr"]["subtitle"], "Fallback Subtitle")

    def test_skills_file_replaces_skill_lines(self):
        skills = [{"category": "Reseaux", "items": "DHCP, DNS."}]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "skills.json"
            path.write_text(json.dumps(skills), encoding="utf-8")
            data = json.loads(json.dumps(MASTER))
            gc.apply_overrides(data, "it_support", "fr", skills_file=str(path))
            tex = gc.build_latex_document(data, "it_support", "fr")
        self.assertIn("Reseaux", tex)
        self.assertNotIn("Vidéosurveillance", tex)

    def test_missing_skills_file_stops_with_clear_error(self):
        with self.assertRaises(SystemExit):
            gc.apply_overrides(json.loads(json.dumps(MASTER)), "it_support", "fr", skills_file="nope.json")

    def test_empty_project_list_drops_the_projects_section(self):
        data = json.loads(json.dumps(MASTER))
        gc.apply_overrides(data, "it_support", "fr", project_ids=[])
        tex = gc.build_latex_document(data, "it_support", "fr")
        self.assertNotIn("\\section{Projets}", tex)
        self.assertIn("\\section{Formation}", tex)

    def test_none_keeps_the_track_default_projects(self):
        tex, _ = self.tailored()
        self.assertIn("\\section{Projets}", tex)


class PdfPageCountTests(unittest.TestCase):
    def test_counts_page_objects_in_raw_pdf(self):
        blob = b"%PDF-1.4\n1 0 obj<</Type /Page /Parent 2 0 R>>endobj\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "one.pdf"
            path.write_bytes(blob)
            # Force the byte-scan path even if pdfinfo exists on the host.
            which = gc.shutil.which
            gc.shutil.which = lambda name: None if name == "pdfinfo" else which(name)
            try:
                self.assertEqual(gc.pdf_page_count(path), 1)
            finally:
                gc.shutil.which = which

    def test_counts_page_objects_inside_flate_stream(self):
        import zlib

        content = b"1 0 obj<</Type/Page/Parent 2 0 R>>endobj"
        stream = zlib.compress(content)
        blob = (
            b"%PDF-1.4\n2 0 obj<< /Length "
            + str(len(stream)).encode()
            + b" /Filter /FlateDecode >>stream\n"
            + stream
            + b"\nendstream\nendobj\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "compressed.pdf"
            path.write_bytes(blob)
            which = gc.shutil.which
            gc.shutil.which = lambda name: None if name == "pdfinfo" else which(name)
            try:
                self.assertEqual(gc.pdf_page_count(path), 1)
            finally:
                gc.shutil.which = which

    def test_rejects_multi_page_pdf(self):
        blob = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type /Page /Parent 3 0 R>>endobj\n"
            b"2 0 obj<</Type /Page /Parent 3 0 R>>endobj\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "two.pdf"
            path.write_bytes(blob)
            which = gc.shutil.which
            gc.shutil.which = lambda name: None if name == "pdfinfo" else which(name)
            try:
                self.assertEqual(gc.pdf_page_count(path), 2)
                err = io.StringIO()
                with redirect_stderr(err):
                    ok = gc.assert_single_page_cv(path)
                self.assertFalse(ok)
                self.assertIn("exactly 1 page", err.getvalue())
            finally:
                gc.shutil.which = which


if __name__ == "__main__":
    unittest.main()
