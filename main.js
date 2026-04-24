const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) entry.target.classList.add('visible');
  });
}, { threshold: 0.1 });
document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

const progressEl = document.getElementById('scrollProgress');
if (progressEl) {
  window.addEventListener('scroll', () => {
    const scrollTop = document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    progressEl.style.width = (scrollTop / scrollHeight * 100) + '%';
  });
}

const typedEl = document.getElementById('typed');
if (typedEl) {
  const phrases = [
    'Maker, tinkerer, biotech by day.',
    'Building tools, gadgets, and things I couldn\'t find for sale.',
    'At the bench, in the water, or somewhere in between.'
  ];
  let phraseIdx = 0, charIdx = 0, isDeleting = false;

  function typeLoop() {
    const current = phrases[phraseIdx];
    if (!isDeleting) {
      typedEl.textContent = current.substring(0, charIdx + 1);
      charIdx++;
      if (charIdx === current.length) {
        isDeleting = true;
        setTimeout(typeLoop, 2200);
        return;
      }
      setTimeout(typeLoop, 40);
    } else {
      typedEl.textContent = current.substring(0, charIdx - 1);
      charIdx--;
      if (charIdx === 0) {
        isDeleting = false;
        phraseIdx = (phraseIdx + 1) % phrases.length;
        setTimeout(typeLoop, 400);
        return;
      }
      setTimeout(typeLoop, 20);
    }
  }
  setTimeout(typeLoop, 800);
}
