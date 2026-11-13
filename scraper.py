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

# ΔΙΟΡΘΩΣΗ: Στοχεύουμε πλέον καθαρά στις ροές των άρθρων, όχι στους καταλόγους ονομάτων
PAGES = {
    "CAPITAL.GR": "https://www.capital.gr/apopseis/", 
    "LIBERAL.GR": "https://www.liberal.gr/apopseis",
    "MONONEWS.GR": "https://www.mononews.gr/category/apopsis",
    "Η ΚΑΘΗΜΕΡΙΝΗ": "https://www.kathimerini.gr/opinions/"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # Προσπαθούμε να πάρουμε τον τίτλο πρώτα από το attribute title (συχνό στην Καθημερινή) 
                # αλλιώς από το κείμενο του link
                title = a_tag.get('title', '').strip()
                if not title:
                    title = a_tag.get_text(strip=True)
                
                # ΑΥΣΤΗΡΟ ΦΙΛΤΡΟ: Αν ο τίτλος έχει λιγότερες από 4 λέξεις, απορρίπτεται αμέσως.
                # Έτσι δεν θα ξαναπιάσει ποτέ ονόματα όπως "Γιώργος Κράλογλου" ως τίτλο.
                if len(title.split()) < 4 or len(title) < 20:
                    continue
                    
                # Αποφυγή γενικών links κατηγοριών
                if href.endswith('/apopseis') or href.endswith('/opinions/'):
                    continue
                    
                parent = a_tag
                found_author = None
                
                # Ψάχνουμε τον αρθρογράφο γύρω από το link (έως 5 "κουτιά" πιο έξω στο HTML)
                for _ in range(5):
                    if not parent: break
                    parent_text = normalize_greek(parent.get_text(separator=' ', strip=True))
                    
                    if len(parent_text) > 800: # Αν διαβάζει όλη τη σελίδα, σταματάμε
                        break
                        
                    for author in AUTHORS[source]:
                        norm_author = normalize_greek(author)
                        norm_author_genitive = norm_author[:-1] if norm_author.endswith('Σ') else norm_author
                        
                        if norm_author in parent_text or norm_author_genitive in parent_text:
                            found_author = author
                            break
                            
                    if found_author:
                        break
                    parent = parent.parent
                    
                if found_author:
                    clean_title = title.replace(f"{found_author}:", "").replace(f"{found_author} :", "").strip()
                    
                    if not href.startswith('http'):
                        if "CAPITAL" in source: href = "https://www.capital.gr" + href
                        elif "LIBERAL" in source: href = "https://www.liberal.gr" + href
                        elif "ΚΑΘΗΜΕΡΙΝΗ" in source: href = "https://www.kathimerini.gr" + href
                        elif "MONONEWS" in source: href = "https://www.mononews.gr" + href
                        
                    articles.append({
                        "source": source,
                        "date": today_str,
                        "title": clean_title,
                        "link": href,
                        "author": found_author
                    })
                    
        except Exception as e:
            print(f"Σφάλμα κατά τη σάρωση: {e}")

    # Αφαίρεση τυχόν διπλών άρθρων
    unique_articles = {article['link']: article for article in articles}.values()
    return list(unique_articles)

if __name__ == "__main__":
    data = fetch_articles()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
