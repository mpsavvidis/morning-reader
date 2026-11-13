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

# ΑΦΑΙΡΕΘΗΚΑΝ οριστικά οι κατάλογοι "arthrografoi". Στοχεύουμε μόνο στα πραγματικά άρθρα.
PAGES = {
    "CAPITAL.GR": ["https://www.capital.gr/apopseis/"],
    "LIBERAL.GR": ["https://www.liberal.gr/apopseis"],
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
            try:
                response = requests.get(url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    
                    title_from_text = a_tag.get_text(separator=' ', strip=True)
                    title_from_attr = a_tag.get('title', '').strip()
                    title = title_from_text if len(title_from_text) > len(title_from_attr) else title_from_attr
                    
                    if href.endswith('/apopseis') or href.endswith('/opinions/') or 'author' in href:
                        continue
                        
                    parent = a_tag
                    found_author = None
                    
                    for _ in range(6):
                        if not parent or parent.name in ['body', 'html', 'main', 'nav', 'footer']:
                            break
                            
                        parent_text = normalize_greek(parent.get_text(separator=' ', strip=True))
                        
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
                        clean_title = title.replace(f"{found_author}:", "").replace(f"{found_author} :", "").strip()
                        if clean_title.upper().startswith(normalize_greek(found_author)):
                            clean_title = clean_title[len(found_author):].strip(" -|:")
                        
                        # ΤΕΛΙΚΟΣ ΑΥΣΤΗΡΟΣ ΕΛΕΓΧΟΣ: Αφού καθαριστεί ο τίτλος, αν έχουν μείνει λιγότερες 
                        # από 4 λέξεις (π.χ. σκέτα ονόματα ή κενά), το απορρίπτουμε οριστικά.
                        if len(clean_title.split()) < 4:
                            continue
                            
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

    # Αν βρεθούν διπλά links, κρατάμε την εγγραφή με τον πιο "πλούσιο/σωστό" τίτλο
    unique_articles = {}
    for article in articles:
        link = article['link']
        if link not in unique_articles or len(article['title']) > len(unique_articles[link]['title']):
            unique_articles[link] = article
            
    return list(unique_articles.values())

if __name__ == "__main__":
    data = fetch_articles()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
