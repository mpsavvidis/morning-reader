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

# Προσθέσαμε πολλαπλές πηγές για να είμαστε σίγουροι ότι "σαρώνουμε" τα πάντα
PAGES = {
    "CAPITAL.GR": ["https://www.capital.gr/apopseis/", "https://www.capital.gr/arthrografoi/"],
    "LIBERAL.GR": ["https://www.liberal.gr/apopseis", "https://www.liberal.gr/arthrografoi"],
    "MONONEWS.GR": ["https://www.mononews.gr/category/apopsis"],
    "Η ΚΑΘΗΜΕΡΙΝΗ": ["https://www.kathimerini.gr/opinions/"]
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
    
    for source, urls in PAGES.items():
        for url in urls:
            print(f"Σάρωση σελίδας: {url}")
            try:
                response = requests.get(url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    
                    # 1η Βελτίωση: Ψάχνει τον τίτλο και στο κείμενο και στα attributes της εικόνας
                    title_from_text = a_tag.get_text(separator=' ', strip=True)
                    title_from_attr = a_tag.get('title', '').strip()
                    # Κρατάει το πιο μεγάλο (το αληθινό)
                    title = title_from_text if len(title_from_text) > len(title_from_attr) else title_from_attr
                    
                    # 2η Βελτίωση: Χαλαρώσαμε το όριο λέξεων για να μην κόβει μικρούς αληθινούς τίτλους
                    if len(title.split()) < 3 or len(title) < 12:
                        continue
                        
                    # Αποφυγή links που είναι απλά κατηγορίες ή προφίλ
                    if href.endswith('/apopseis') or href.endswith('/opinions/') or 'author' in href:
                        continue
                        
                    parent = a_tag
                    found_author = None
                    
                    # Ανεβαίνουμε το HTML δέντρο για να βρούμε τον αρθρογράφο δίπλα στο link
                    for _ in range(6):
                        if not parent or parent.name in ['body', 'html', 'main', 'nav', 'footer']:
                            break
                            
                        parent_text = normalize_greek(parent.get_text(separator=' ', strip=True))
                        
                        # 3η Βελτίωση: Αυξήσαμε το όριο στους 1500 χαρακτήρες για να χωράνε άρθρα με μεγάλη περίληψη
                        if len(parent_text) > 1500:
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
                        # Καθαρισμός τίτλου αν περιέχει το όνομα μέσα (π.χ. "Μ. Καψής: Ο τίτλος")
                        clean_title = title.replace(f"{found_author}:", "").replace(f"{found_author} :", "").strip()
                        if clean_title.upper().startswith(normalize_greek(found_author)):
                            clean_title = clean_title[len(found_author):].strip(" -|:")
                        
                        # Διόρθωση URL αν λείπει το https
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

    # Αφαίρεση τυχόν διπλοεγγραφών (αν το βρήκε 2 φορές σε διαφορετικά URLs του ίδιου site)
    unique_articles = {article['link']: article for article in articles}.values()
    return list(unique_articles)

if __name__ == "__main__":
    data = fetch_articles()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
