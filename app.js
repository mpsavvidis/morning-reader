document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('articles-container');
    const updatedText = document.getElementById('last-updated');
    const loader = document.getElementById('loader');

    try {
        // Διαβάζουμε το data.json, με παραμέτρους για αποφυγή cache
        const response = await fetch(`data.json?v=${new Date().getTime()}`); 
        const articles = await response.json();

        // Εξαφανίζουμε το κείμενο φόρτωσης
        if (loader) loader.remove();

        if (articles.length === 0) {
            container.innerHTML = `
                <div class="bg-white rounded-2xl p-10 text-center border border-slate-100 shadow-sm">
                    <p class="text-slate-500 font-medium">Δεν βρέθηκαν νέα άρθρα για σήμερα.</p>
                    <p class="text-sm text-slate-400 mt-2">Επόμενη αυτόματη ανανέωση αύριο στις 06:30.</p>
                </div>
            `;
            return;
        }

        updatedText.textContent = `Ενημέρωση: Σήμερα, 06:30`;

        // Χρώματα για τα "ταμπελάκια" (badges) των πηγών
        const sourceColors = {
            "CAPITAL.GR": "bg-blue-50 text-blue-700 border-blue-100",
            "LIBERAL.GR": "bg-orange-50 text-orange-700 border-orange-100",
            "MONONEWS.GR": "bg-emerald-50 text-emerald-700 border-emerald-100",
            "Η ΚΑΘΗΜΕΡΙΝΗ": "bg-red-50 text-red-700 border-red-100"
        };

        articles.forEach(article => {
            const item = document.createElement('article');
            // Σχεδιασμός κάρτας
            item.className = 'bg-white rounded-2xl p-5 sm:p-6 shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)] border border-slate-200 hover:shadow-lg hover:border-slate-300 transition-all duration-300 group';
            
            // Το αρχικό γράμμα του αρθρογράφου
            const initial = article.author.charAt(0).toUpperCase();
            
            // Επιλογή χρώματος ανάλογα με την πηγή (ή default γκρι)
            const badgeStyle = sourceColors[article.source] || "bg-slate-100 text-slate-700 border-slate-200";

            item.innerHTML = `
                <div class="flex items-center justify-between mb-4">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-md text-[10px] font-bold tracking-widest uppercase border ${badgeStyle}">
                        ${article.source}
                    </span>
                    <span class="text-xs text-slate-400 font-medium tracking-wide">${article.date}</span>
                </div>
                
                <h2 class="text-xl sm:text-2xl font-serif font-bold leading-tight mb-4 text-slate-900 group-hover:text-indigo-700 transition-colors">
                    <a href="${article.link}" target="_blank" class="before:absolute before:inset-0 relative">${article.title}</a>
                </h2>
                
                <div class="flex items-center gap-3 mt-4 pt-4 border-t border-slate-100 relative z-10">
                    <div class="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center text-white font-bold text-xs shadow-sm">
                        ${initial}
                    </div>
                    <p class="text-sm font-semibold text-slate-700">${article.author}</p>
                </div>
            `;
            // CSS trick (before:absolute) για να κάνει όλη την κάρτα κλικαρίσιμη, όχι μόνο τον τίτλο.
            item.style.position = 'relative'; 

            container.appendChild(item);
        });

    } catch (error) {
        console.error("Σφάλμα:", error);
        if (loader) loader.remove();
        container.innerHTML = `
            <div class="bg-red-50 rounded-2xl p-6 text-center border border-red-100">
                <p class="text-red-600 font-medium">Υπήρξε σφάλμα κατά τη φόρτωση.</p>
                <p class="text-sm text-red-400 mt-1">Παρακαλώ ανανεώστε τη σελίδα.</p>
            </div>
        `;
    }
});