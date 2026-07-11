import argparse
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "skill/word-safe-editing/scripts/check_docx_safety.py"
SPEC = importlib.util.spec_from_file_location("checker", SCRIPT)
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"

def args(**overrides):
    defaults = dict(must_contain=[], must_not_contain=[], expect_text_count=[],
        forbid_images_between=None, forbid_figure_captions_between=None,
        max_row_height_between=None, warn_unreferenced_media=False,
        fail_on_warnings=False)
    defaults.update(overrides)
    return argparse.Namespace(**defaults)

def make_docx(path, text="Hello safety", document_rels=None, malformed=False):
    doc = ("<w:document" if malformed else
        f'<?xml version="1.0"?><w:document xmlns:w="{W}"><w:body>'
        f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p><w:sectPr/>"
        "</w:body></w:document>")
    root_rels = (f'<?xml version="1.0"?><Relationships xmlns="{REL}">'
        '<Relationship Id="rId1" Type="officeDocument" Target="word/document.xml"/>'
        "</Relationships>")
    with ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("_rels/.rels", root_rels)
        z.writestr("word/document.xml", doc)
        if document_rels:
            z.writestr("word/_rels/document.xml.rels", document_rels)

class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "中文 sample.docx"

    def tearDown(self):
        self.tmp.cleanup()

    def codes(self, **kwargs):
        return {i.code for i in checker.check_docx(self.path, args(**kwargs))}

    def test_valid_docx_and_unicode_path(self):
        make_docx(self.path)
        self.assertEqual(self.codes(must_contain=["Hello safety"]), set())

    def test_required_and_forbidden_text(self):
        make_docx(self.path)
        self.assertIn("missing-required-text", self.codes(must_contain=["Missing"]))
        self.assertIn("forbidden-text", self.codes(must_not_contain=["Hello"]))

    def test_text_count(self):
        make_docx(self.path, "alpha alpha")
        self.assertIn("unexpected-text-count", self.codes(expect_text_count=["alpha=1"]))

    def test_malformed_xml(self):
        make_docx(self.path, malformed=True)
        self.assertIn("invalid-xml", self.codes())

    def test_missing_relationship_target(self):
        rels = (f'<Relationships xmlns="{REL}">'
            '<Relationship Id="rId2" Type="image" Target="media/missing.png"/>'
            "</Relationships>")
        make_docx(self.path, document_rels=rels)
        self.assertIn("missing-relationship-target", self.codes())

    def test_bad_zip(self):
        self.path.write_bytes(b"not a zip")
        self.assertIn("bad-zip", self.codes())

    def test_missing_file(self):
        self.assertIn("missing-file", self.codes())

if __name__ == "__main__":
    unittest.main()
