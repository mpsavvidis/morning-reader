import json
import feedparser
from datetime import datetime
import unicodedata

AUTHORS = {
    "CAPITAL.GR": ["Μανόλης Καψής", "Άγης Βερούτης", "Λέανδρος Ρακιντζής", "Θάνος Τζήμερος", "Χρήστος Χωμενίδης", "Ηλίας Παπαγεωργιάδης", "Γεώργιους Ι. Μάτσος", "Γιάννης Πανούσης", "Ηλίας Ψυχογιός", "Γιώργος Ι. Κωστούλας"],
    "LIBERAL.GR": ["Θανάσης Μαυρίδης", "Κώστας Στούπας", "Γιώργος Βουλγαράκης", "Σάκης Μουμτζής", "Αλέξανδρος Σκούρας", "Ζαχαρίας Ζούπης"],
    "MONONEWS.GR": ["The Wiseman", "ROOM 301", "Αντώνης Κεφαλάς", "Λώρη Κέζα"],
    "Η ΚΑΘΗΜΕΡΙΝΗ": ["Αλέξης Παπαχελάς", "Τάκης Θεοδωρόπουλος", "Μιχάλης Τσιντσίνης", "Κώστας Ιορδανίδης", "Αθανάσιος Έλλις", "Νίκος Κωνσταντάρας", "Παντελής Μπουκάλας", "Τασούλα Καραϊσκάκη", "Ανδρέας Δρυμιώτης", "Μαρία Κατσουνάκη", "Νότης Παπαδόπουλος", "Κώστας Λεονταρίδης", "Ηλίας Μαγκλίνης", "Ξένια Κουναλάκη", "Παναγιώτης Λάμψιας", "Σάκης Μουμτζής", "Κώστας Καλλίτσης", "Άρης Αλεξανδρής", "Θοδωρής Γεωργακόπουλος", "Στάθης Ν. Καλύβας", "Δώρα Αντωνίου", "Γιούλη Επτακοίλη", "Ελεάννα Βλαστού", "Αριστείδης Χατζής", "Χαρίδημος Τσούκας", "Βίβιαν Στεργίου"]
}

RSS_FEEDS = {
    "CAPITAL.GR": "https://www.capital.gr/rss/arthrografoi",
    "LIBERAL.GR": "https://www.liberal.gr/rss",
    "MONONEWS.GR": "https://www.mononews.gr/feed",
    "Η ΚΑΘΗΜΕΡΙΝΗ": "https://www.kathimerini.gr/opinions/feed/"
}

def normalize_greek(text):
    """Αφαιρεί τόνους και μετατρέπει σε κεφαλαία για ακριβή ταύτιση."""
    if not text:
        return ""
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return text.upper()

def fetch_articles():
    articles = []
    today_str = datetime.now().strftime("%d.%m.%Y")
    
    for source, feed_url in RSS_FEEDS.items():
        parsed_feed = feedparser.parse(feed_url)
        
        for entry in parsed_feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            entry_author = entry.get("author", "")
            summary = entry.get("summary", "")
            
            # Ενοποιούμε όλα τα πεδία όπου μπορεί να αναφέρεται ο αρθρογράφος
            search_text = normalize_greek(f"{title} {entry_author} {summary}")
            
            for author in AUTHORS[source]:
                norm_author = normalize_greek(author)
                
                # Δημιουργία της γενικής πτώσης αφαιρώντας το τελικό Σίγμα
                norm_author_genitive = norm_author[:-1] if norm_author.endswith('Σ') else norm_author
                
                # Έλεγχος αν το όνομα υπάρχει στο άρθρο στην ονομαστική ή τη γενική
                if norm_author in search_text or norm_author_genitive in search_text:
                    
                    # Καθαρισμός τίτλου για καλύτερη εμφάνιση (αν ξεκινάει με το όνομα)
                    clean_title = title.replace(f"{author}:", "").replace(f"{author} :", "").strip()
                    
                    articles.append({
                        "source": source,
                        "date": today_str,
                        "title": clean_title,
                        "link": link,
                        "author": author
                    })
                    break 

    # Κρατάμε μόνο τα μοναδικά links για να αποφύγουμε διπλοεγγραφές
    unique_articles = {article['link']: article for article in articles}.values()
    return list(unique_articles)

if __name__ == "__main__":
    data = fetch_articles()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
