import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

AUTHORS = {
    "CAPITAL.GR": ["Μανόλης Καψής", "Άγης Βερούτης", "Λέανδρος Ρακιντζής", "Θάνος Τζήμερος", "Χρήστος Χωμενίδης", "Ηλίας Παπαγεωργιάδης", "Γεώργιους Ι. Μάτσος", "Γιάννης Πανούσης", "Ηλίας Ψυχογιός", "Γιώργος Ι. Κωστούλας"],
    "LIBERAL.GR": ["Θανάσης Μαυρίδης", "Κώστας Στούπας", "Γιώργος Βουλγαράκης", "Σάκης Μουμτζής", "Αλέξανδρος Σκούρας", "Ζαχαρίας Ζούπης"],
    "MONONEWS.GR": ["The Wiseman", "ROOM 301", "Αντώνης Κεφαλάς", "Λώρη Κέζα"],
    "Η ΚΑΘΗΜΕΡΙΝΗ": ["Αλέξης Παπαχελάς", "Τάκης Θεοδωρόπουλος", "Μιχάλης Τσιντσίνης", "Κώστας Ιορδανίδης", "Αθανάσιος Έλλις", "Νίκος Κωνσταντάρας", "Παντελής Μπουκάλας", "Τασούλα Καραϊσκάκη", "Ανδρέας Δρυμιώτης", "Μαρία Κατσουνάκη", "Νότης Παπαδόπουλος", "Κώστας Λεονταρίδης", "Ηλίας Μαγκλίνης", "Ξένια Κουναλάκη", "Παναγιώτης Λάμψιας", "Σάκης Μουμτζής", "Κώστας Καλλίτσης", "Άρης Αλεξανδρής", "Θοδωρής Γεωργακόπουλος", "Στάθης Ν. Καλύβας", "Δώρα Αντωνίου", "Γιούλη Επτακοίλη", "Ελεάννα Βλαστού", "Αριστείδης Χατζής", "Χαρίδημος Τσούκας", "Βίβιαν Στεργίου"]
}

def fetch_articles():
    articles = []
    today = datetime.now().strftime("%d.%m.%Y")
    
    # TODO: Εδώ προσθέτεις την ακριβή λογική με BeautifulSoup για κάθε site
    # Παράδειγμα χρήσης: 
    # response = requests.get("https://www.capital.gr/arthrografoi/", headers=HEADERS)
    # soup = BeautifulSoup(response.content, "html.parser")
    # ... αναζήτηση τίτλων και ελέγχος αν ανήκουν στη λίστα AUTHORS["CAPITAL.GR"] ...

    # Προσωρινά δεδομένα (mock data) για να λειτουργήσει το UI στην πρώτη εκτέλεση
    articles.append({
        "source": "CAPITAL.GR",
        "date": today,
        "title": "Η επόμενη μέρα της οικονομίας και οι προκλήσεις (Δοκιμαστικό)",
        "link": "https://www.capital.gr",
        "author": "Μανόλης Καψής"
    })
    articles.append({
        "source": "Η ΚΑΘΗΜΕΡΙΝΗ",
        "date": today,
        "title": "Οι μεταρρυθμίσεις που χρειάζεται η χώρα (Δοκιμαστικό)",
        "link": "https://www.kathimerini.gr",
        "author": "Αλέξης Παπαχελάς"
    })

    return articles

if __name__ == "__main__":
    print("Ξεκινάει η συλλογή άρθρων...")
    data = fetch_articles()
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Ολοκληρώθηκε. Αποθηκεύτηκαν {len(data)} άρθρα.")