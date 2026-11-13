import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata

AUTHORS = {
    "CAPITAL.GR": ["Μανόλης Καψής", "Άγης Βερούτης", "Λέανδρος Ρακιντζής", "Θάνος Τζήμερος", "Χρήστος Χωμενίδης", "Ηλίας Παπαγεωργιάδης", "Γεώργιους Ι. Μάτσος", "Γιάννης Πανούσης", "Ηλίας Ψυχογιός", "Γιώργος Ι. Κωστούλας"],
    "LIBERAL.GR": ["Θανάσης Μαυρίδης", "Κώστας Στούπας", "Γιώργος Βουλγαράκης", "Σάκης Μουμτζής", "Αλέξανδρος Σκούρας", "Ζαχαρίας Ζούπης"],
    "MONONEWS.GR": ["The Wiseman", "ROOM 301", "Αντώνης Κεφαλάς", "Λώρη Κέζα"],
    "Η ΚΑΘΗΜΕΡΙΝΗ": ["Αλέξης Παπαχελάς", "Τάκης Θεοδωρόπουλος", "Μιχάλης Τσιντσίνης", "Κώστας Ιορδανίδης", "Αθανάσιος Έλλις", "Νίκος Κωνσταντάρας", "Παντελής Μπουκάλας", "Τασούλα Καραϊσκάκη", "Ανδρέας Δρυμιώτης", "Μαρία Κατσουνάκη", "Νότης Παπαδόπουλος", "Κώστας Λεονταρίδης", "Ηλίας Μαγκλίνης", "Ξένια Κουναλάκη", "Παναγιώτης Λάμψιας", "Σάκης Μουμτζής", "Κώστας Καλλίτσης", "Άρης Αλεξανδρής", "Θοδωρής Γεωργακόπουλος", "Στάθης Ν. Καλύβας", "Δώρα Αντωνίου", "Γιούλη Επτακοίλη", "Ελεάννα Βλαστού", "Αριστείδης Χατζής", "Χαρίδημος Τσούκας", "Βίβιαν Στεργίου"]
}

# Οι κεντρικές σελίδες των αρθρογράφων που βλέπεις και εσύ
PAGES = {
    "CAPITAL.GR": "https://www.capital.gr/arthrografoi/",
    "LIBERAL.GR": "https://www.liberal.gr/apopseis",
    "MONONEWS.GR": "https://www.mononews.gr/category/apopsis",
    "Η ΚΑΘΗΜΕΡΙΝΗ": "https://www.kathimerini.gr/opinions/"
}

# Κάνουμε το script να μοιάζει με κανονικό browser (Chrome)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "el-GR,el;q=0.9,en-US;q=0.8,en;q=0.7",
}

def normalize_greek(text):
    if not text: return ""
    text = ''.join(c for c in unicodedata.normalize('NFD', str(text)) if unicodedata.category(c) != 'Mn')
    return text.upper()

def fetch_articles():
    articles = []
    today_str = datetime.now().strftime("%d.%m.%Y")
    
    for source, url in PAGES.items():
        print(f"Σάρωση σελίδας: {source}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ψάχνουμε όλα τα links στη σελίδα
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                title = a_tag.get_text(strip=True)
                
                # Αγνοούμε πολύ μικρά links (πχ. Μενού)
                if len(title) < 15 or len(href) < 10:
                    continue
                    
                # Ψάχνουμε αν το όνομα του αρθρογράφου βρίσκεται κοντά στον τίτλο (στον "γονέα" του HTML)
                parent = a_tag
                found_author = None
                
                for _ in range(4):
                    if not parent: break
                    # Αποφεύγουμε τεράστια μπλοκ κειμένου
                    if len(parent.get_text(strip=True)) > 500:
                        break
                        
                    parent_text = normalize_greek(parent.get_text(separator=' ', strip=True))
                    
                    for author in AUTHORS[source]:
                        norm_author = normalize_greek(author)
                        # Υποστήριξη και για ονομαστική και για γενική πτώση (π.χ. Παπαχελάς -> Παπαχελά)
                        norm_author_genitive = norm_author[:-1] if norm_author.endswith('Σ') else norm_author
                        
                        if norm_author in parent_text or norm_author_genitive in parent_text:
                            found_author = author
                            break
                            
                    if found_author:
                        break
                    parent = parent.parent
                    
                if found_author:
                    # Καθαρισμός του τίτλου 
                    clean_title = title.replace(f"{found_author}:", "").replace(f"{found_author} :", "").strip()
                    if clean_title.startswith(found_author):
                        clean_title = clean_title.replace(found_author, "").strip(" -|:")
                        
                    # Διόρθωση των links που δεν ξεκινούν με https (relative links)
                    if not href.startswith('http'):
                        if "CAPITAL" in source: href = "https://www.capital.gr" + href
                        elif "LIBERAL" in source: href = "https://www.liberal.gr" + href
                        elif "ΚΑΘΗΜΕΡΙΝΗ" in source: href = "https://www.kathimerini.gr" + href
                        
                    articles.append({
                        "source": source,
                        "date": today_str,
                        "title": clean_title,
                        "link": href,
                        "author": found_author
                    })
                    
        except Exception as e:
            print(f"Σφάλμα κατά τη σάρωση του {source}: {e}")

    # Αφαιρούμε διπλοεγγραφές (αν το ίδιο άρθρο εμφανίζεται 2 φορές στην ίδια σελίδα)
    unique_articles = {article['link']: article for article in articles}.values()
    return list(unique_articles)

if __name__ == "__main__":
    print("Έναρξη Scraping...")
    data = fetch_articles()
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Τέλος! Βρέθηκαν {len(data)} άρθρα συνολικά.")
