import json
import zipfile
import sys
import datetime

from kanjinetworks import get_text, KanjiNetworksParser

from pdfminer.high_level import extract_text
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



def extract_and_save_intro(pdf_path, intro_file):

    # pdfminer uses 0-based indexing for pages.
    target_pages = [0, 1, 2, 3, 4, 5, 6]
    intro_text = extract_text(pdf_path, page_numbers=target_pages)
    
    with open(intro_file, 'w', encoding='utf-8') as f:
        f.write(intro_text.strip())
        
    print(f"Introduction saved to '{intro_file}'.")

def build_kanji_bank(kanjis):
    """Formats parsed objects into Yomitan v3 kanji schema."""
    kanji_bank = []
    
    for obj in kanjis:
        if isinstance(obj, dict):
            char = obj.get('kanji') or obj.get('character', "")
            etym = obj.get('etymology') or obj.get('meaning', str(obj))
        else:
            char = getattr(obj, 'kanji', getattr(obj, 'character', ""))
            etym = getattr(obj, 'etymology', getattr(obj, 'meaning', str(obj)))

        if not char:
            continue

        # Yomitan format: [character, onyomi, kunyomi, tags, meanings, stats]
        kanji_bank.append([char, "", "", "etymology", [etym], {}])
        
    return kanji_bank

def save_yomitan_dictionary(kanji_bank, output_dir):
    """Writes index and bank JSONs, then packages them into a Zip file."""
    output_zip = f"{output_dir}/KanjiNetworks_Yomitan.zip"
    index_file = f"{output_dir}/index.json"
    bank_file  = f"{output_dir}/kanji_bank_1.json"

    try:
        # Write uncompressed files for debugging
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_metadata, f, ensure_ascii=False, indent=2)
            
        with open(bank_file, 'w', encoding='utf-8') as f:
            json.dump(kanji_bank, f, ensure_ascii=False, separators=(',', ':'))

        # Archive files
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(index_file, arcname='index.json')
            zipf.write(bank_file, arcname='kanji_bank_1.json')
            
        print(f"Exported {len(kanji_bank)} entries to '{output_zip}'.")
        print(f"Uncompressed JSON files retained in '{output_dir}/' for debugging.")
        
    except IOError as e:
        sys.exit(f"Failed to write output files: {e}")

def main(output_dir="out"):
    print("Fetching and parsing Kanji Networks PDF...")

    text = get_text()
    kanjis = list(KanjiNetworksParser().parse(text))

    if not kanjis:
        sys.exit("Error: No kanji found in the parsed text.")

    extract_and_save_intro(PDF_PATH, f"{output_dir}/introduction.txt")
    
    kanji_bank = build_kanji_bank(kanjis)
    
    save_yomitan_dictionary(kanji_bank, output_dir)

if __name__ == '__main__':
    main()