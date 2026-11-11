import json
import feedparser
from datetime import datetime
import time

AUTHORS = {
    "CAPITAL.GR": ["Μανόλης Καψής", "Άγης Βερούτης", "Λέανδρος Ρακιντζής", "Θάνος Τζήμερος", "Χρήστος Χωμενίδης", "Ηλίας Παπαγεωργιάδης", "Γεώργιους Ι. Μάτσος", "Γιάννης Πανούσης", "Ηλίας Ψυχογιός", "Γιώργος Ι. Κωστούλας"],
    "LIBERAL.GR": ["Θανάσης Μαυρίδης", "Κώστας Στούπας", "Γιώργος Βουλγαράκης", "Σάκης Μουμτζής", "Αλέξανδρος Σκούρας", "Ζαχαρίας Ζούπης"],
    "MONONEWS.GR": ["The Wiseman", "ROOM 301", "Αντώνης Κεφαλάς", "Λώρη Κέζα"],
    "Η ΚΑΘΗΜΕΡΙΝΗ": ["Αλέξης Παπαχελάς", "Τάκης Θεοδωρόπουλος", "Μιχάλης Τσιντσίνης", "Κώστας Ιορδανίδης", "Αθανάσιος Έλλις", "Νίκος Κωνσταντάρας", "Παντελής Μπουκάλας", "Τασούλα Καραϊσκάκη", "Ανδρέας Δρυμιώτης", "Μαρία Κατσουνάκη", "Νότης Παπαδόπουλος", "Κώστας Λεονταρίδης", "Ηλίας Μαγκλίνης", "Ξένια Κουναλάκη", "Παναγιώτης Λάμψιας", "Σάκης Μουμτζής", "Κώστας Καλλίτσης", "Άρης Αλεξανδρής", "Θοδωρής Γεωργακόπουλος", "Στάθης Ν. Καλύβας", "Δώρα Αντωνίου", "Γιούλη Επτακοίλη", "Ελεάννα Βλαστού", "Αριστείδης Χατζής", "Χαρίδημος Τσούκας", "Βίβιαν Στεργίου"]
}

# Επίσημες ροές RSS για άρθρα/απόψεις των συγκεκριμένων sites
RSS_FEEDS = {
    "CAPITAL.GR": "https://www.capital.gr/rss/arthrografoi",
    "LIBERAL.GR": "https://www.liberal.gr/rss",
    "MONONEWS.GR": "https://www.mononews.gr/feed",
    "Η ΚΑΘΗΜΕΡΙΝΗ": "https://www.kathimerini.gr/opinions/feed/"
}

def fetch_articles():
    articles = []
    today_str = datetime.now().strftime("%d.%m.%Y")
    
    for source, feed_url in RSS_FEEDS.items():
        print(f"Συλλογή από: {source}")
        parsed_feed = feedparser.parse(feed_url)
        
        for entry in parsed_feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            # Προσπαθούμε να βρούμε τον συγγραφέα είτε από το tag author είτε αν αναφέρεται μέσα στον τίτλο
            entry_author = entry.get("author", "").upper()
            
            # Έλεγχος αν κάποιος από τους επιθυμητούς αρθρογράφους ταιριάζει με το άρθρο
            for author in AUTHORS[source]:
                # Ψάχνουμε το όνομα είτε στο πεδίο του συγγραφέα είτε στον τίτλο (π.χ. "Αλέξης Παπαχελάς: Ο τίτλος")
                if author.upper() in entry_author or author.upper() in title.upper():
                    
                    # Καθαρισμός του τίτλου αν περιέχει το όνομα του αρθρογράφου στην αρχή
                    clean_title = title.replace(f"{author}:", "").replace(f"{author} :", "").strip()
                    
                    articles.append({
                        "source": source,
                        "date": today_str,
                        "title": clean_title,
                        "link": link,
                        "author": author
                    })
                    break # Βρέθηκε ο αρθρογράφος, προχωράμε στο επόμενο άρθρο

    # Κρατάμε μόνο τα μοναδικά άρθρα σε περίπτωση διπλοεγγραφών
    unique_articles = {article['link']: article for article in articles}.values()
    return list(unique_articles)

if __name__ == "__main__":
    print("Ξεκινάει η πραγματική συλλογή άρθρων...")
    data = fetch_articles()
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Ολοκληρώθηκε. Βρέθηκαν {len(data)} σημερινά άρθρα από τους αρθρογράφους σου.")
