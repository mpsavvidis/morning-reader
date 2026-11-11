document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('articles-container');
    const updatedText = document.getElementById('last-updated');

    try {
        // Χρήση cache-busting για να αποφύγουμε να δείχνει το κινητό παλιά δεδομένα
        const response = await fetch(`data.json?v=${new Date().getTime()}`); 
        const articles = await response.json();

        if (articles.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-sm font-mono">Δεν βρέθηκαν νέα άρθρα.</p>';
            return;
        }

        updatedText.textContent = `Τελευταία ενημέρωση: Σήμερα, 06:30`;

        articles.forEach(article => {
            const item = document.createElement('article');
            item.className = 'pb-5 border-b border-gray-100 last:border-0';
            
            item.innerHTML = `
                <div class="flex items-baseline gap-2 mb-1.5">
                    <span class="text-[11px] font-mono uppercase tracking-widest text-gray-500">${article.source}</span>
                    <span class="text-[11px] text-gray-400">&bull; ${article.date}</span>
                </div>
                <h2 class="text-lg font-medium leading-snug mb-1">
                    <a href="${article.link}" target="_blank" class="hover:underline decoration-gray-400 underline-offset-4">${article.title}</a>
                </h2>
                <p class="text-sm text-gray-600">
                    <span class="font-medium text-gray-900">${article.author}</span>
                </p>
            `;
            container.appendChild(item);
        });

    } catch (error) {
        console.error("Σφάλμα:", error);
        container.innerHTML = '<p class="text-red-500 text-sm font-mono">Αδυναμία φόρτωσης άρθρων. Ελέγξτε το data.json.</p>';
    }
});