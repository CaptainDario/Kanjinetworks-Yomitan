import os
import re

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


# http://www.slideshare.net/KanjiNetworks/etymological-dictionary-ofhanchinesecharacters

pdf_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/etymologicaldictionaryofhanchinesecharacters-160816005400.pdf")
pdf_range = range(7, 569)


def get_text_from_pdf(path, pagenos=set()):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    for page in PDFPage.get_pages(fp, pagenos, caching=True, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

def sanitize_text(text):
    text = re.sub(u'(\N{COPYRIGHT SIGN}|\N{TRADE MARK SIGN}|\N{REGISTERED SIGN}) 20.*', '', text)
    return text

def get_cache_path():
    root, ext = os.path.splitext(pdf_path)
    return root + ".txt"

def get_text(caching=True, sanitize=True, text_cache_path=get_cache_path(), pdf_range=pdf_range):
    if caching:
        if not os.path.isfile(text_cache_path):
            text = get_text_from_pdf(pdf_path, pagenos=set(pdf_range))
            if sanitize:
                text = sanitize_text(text)
            with open(text_cache_path, "w", encoding="utf-8") as text_file:
                text_file.write(text)
        else:
            with open(text_cache_path, "r", encoding="utf-8") as text_file:
                text = text_file.read()
    else:
        text = get_text_from_pdf(pdf_path, pagenos=set(pdf_range))
    return text

if __name__ == "__main__":
    text = get_text()
    print(text)


import unittest
import tempfile

class TestExtractor(unittest.TestCase):

    def test_get_text_no_cache(self):
        text = get_text(caching=False, pdf_range=range(7, 8))
        self.assertNotEqual(len(text), 0)
        self.assertIsInstance(text, str)

    def test_get_text_cache(self):

        handle, temp_path = tempfile.mkstemp(suffix=".txt", prefix="kanjinetwork_tests_")
        os.close(handle)
        os.unlink(temp_path)

        text = get_text(caching=True, text_cache_path=temp_path, pdf_range=range(7, 8))
        self.assertNotEqual(len(text), 0)
        self.assertIsInstance(text, str)

        text = get_text(caching=True, text_cache_path=temp_path, pdf_range=range(7, 8))
        self.assertNotEqual(len(text), 0)
        self.assertIsInstance(text, str)

        os.unlink(temp_path)