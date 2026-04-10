import json
import zipfile
import sys
import datetime
import shutil

from kanjinetworks import get_text, KanjiNetworksParser

from pypdf import PdfReader, PdfWriter
import os


PDF_PATH = "kanjinetworks_source/kanjinetworks/data/etymologicaldictionaryofhanchinesecharacters-160816005400.pdf"

index_metadata = {
        "title": "Kanji Networks Etymology",
        "format": 3,
        "revision": datetime.datetime.now().strftime("%Y-%m-%d"),
        "sequenced": False,
        "author": "Lawrence J. Howell",
        "url": "http://www.kanjinetworks.com",
        "description": "Etymological Dictionary of Han/Chinese Characters.",
        "attribution": "Lawrence J. Howell / Hikaru Morimoto"
    }


def extract_and_save_intro(pdf_path, intro_pdf_file):
    """Extracts the first 7 pages of the source PDF into a new PDF file."""
    if not os.path.exists(pdf_path):
        print(f"Warning: PDF not found at '{pdf_path}'. Cannot create manual PDF.")
        return

    print(f"Extracting first 7 pages from '{pdf_path}' to '{intro_pdf_file}'...")
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # Extract pages 1-7 (index 0 to 6)
        for page_num in range(min(7, len(reader.pages))):
            writer.add_page(reader.pages[page_num])

        with open(intro_pdf_file, "wb") as f:
            writer.write(f)
            
        print(f"Manual (Introduction) PDF saved to '{intro_pdf_file}'.")
    except Exception as e:
        print(f"Failed to create manual (introduction) PDF: {e}")

def build_kanji_bank(kanjis):
    """Formats parsed Kanji objects into Yomitan v3 kanji schema."""
    kanji_bank = []
    
    for obj in kanjis:
        if isinstance(obj, dict):
            char = obj.get('kanji') or obj.get('character', "")
            definition = obj.get('definition') or obj.get('etymology') or obj.get('meaning', str(obj))
        else:
            char = getattr(obj, 'kanji', getattr(obj, 'character', ""))
            definition = getattr(obj, 'definition', None) or getattr(obj, 'etymology', None) or str(obj)

        if not char:
            continue

        # Yomitan format: [character, onyomi, kunyomi, tags, meanings, stats]
        kanji_bank.append([char, "", "", "etymology", [definition], {}])
        
    return kanji_bank

def verify_kanji_bank(bank_file):
    """Reads back the written kanji bank JSON and prints a quick sanity check."""
    try:
        with open(bank_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total = len(data)
        empty_def = sum(1 for e in data if not e[4] or not e[4][0])
        print(f"Kanji bank verification — total entries: {total}, entries with empty definition: {empty_def}")
        print("  Sample entries:")
        for entry in data[:3]:
            char, _, _, _, meanings, _ = entry
            snippet = (meanings[0] or "")[:120].replace('\n', ' ')
            print(f"    {char}: {snippet}")
    except Exception as e:
        print(f"Kanji bank verification failed: {e}")

def save_yomitan_dictionary(kanji_bank, tmp_dir, output_dir):
    """Writes index and bank JSONs to tmp/, then packages them into a Zip in out/."""
    yomitan_zip = f"{output_dir}/KanjiNetworks_Yomitan.zip"
    dadb_zip   = f"{output_dir}/KanjiNetworks_DaDb.zip"
    index_file = f"{tmp_dir}/index.json"
    bank_file  = f"{tmp_dir}/kanji_bank_1.json"

    try:
        os.makedirs(tmp_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Write uncompressed files to tmp/ for debugging
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_metadata, f, ensure_ascii=False, indent=2)
            
        with open(bank_file, 'w', encoding='utf-8') as f:
            json.dump(kanji_bank, f, ensure_ascii=False, separators=(',', ':'))

        verify_kanji_bank(bank_file)

        # Archive files into the output directory
        for z in [yomitan_zip, dadb_zip]:
            with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(index_file, arcname='index.json')
                zipf.write(bank_file, arcname='kanji_bank_1.json')
                if z == dadb_zip:
                    zipf.write(f"{tmp_dir}/manual.pdf", arcname='manual.pdf')

            
        print(f"Exported {len(kanji_bank)} entries to '{yomitan_zip}'/'{dadb_zip}'.")
        print(f"Uncompressed JSON files retained in '{tmp_dir}/' for debugging.")
        
    except IOError as e:
        sys.exit(f"Failed to write output files: {e}")

def main(tmp_dir="tmp", output_dir="out"):
    print("Fetching and parsing Kanji Networks PDF...")

    text = get_text()
    kanjis = list(KanjiNetworksParser().parse(text))

    if not kanjis:
        sys.exit("Error: No kanji found in the parsed text.")

    os.makedirs(output_dir, exist_ok=True)
    extract_and_save_intro(PDF_PATH, f"{tmp_dir}/manual.pdf")
    
    kanji_bank = build_kanji_bank(kanjis)
    
    save_yomitan_dictionary(kanji_bank, tmp_dir, output_dir)

if __name__ == '__main__':
    main()