function initRating(elementId) {
    const element = document.getElementById(elementId);
    const stars = element.querySelectorAll('.star');
    
    stars.forEach((star, index) => {
        star.addEventListener('click', () => {
            const rating = index + 1;
            stars.forEach((s, i) => {
                s.classList.toggle('active', i < rating);
            });
            document.getElementById('rating').value = rating;
        });
    });
}
