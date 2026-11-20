const fadeEls = document.querySelectorAll('.fade-in');
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add('visible');
    });
  }, { threshold: 0.1 });
  fadeEls.forEach(el => observer.observe(el));
} else {
  fadeEls.forEach(el => el.classList.add('visible'));
}

const progressEl = document.getElementById('scrollProgress');
if (progressEl) {
  window.addEventListener('scroll', () => {
    const scrollTop = document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    progressEl.style.width = (scrollTop / scrollHeight * 100) + '%';
  });
}

const contactSection = document.getElementById('contact');
const homeLink = document.querySelector('nav .links a[href="index.html"], nav .links a[href="#"]');
const contactLink = document.querySelector('nav .links a[href="#contact"]');
if (contactSection && homeLink && contactLink) {
  const spy = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        homeLink.classList.remove('active');
        contactLink.classList.add('active');
      } else {
        contactLink.classList.remove('active');
        homeLink.classList.add('active');
      }
    });
  }, { rootMargin: '-40% 0px -40% 0px' });
  spy.observe(contactSection);
}

const typedEl = document.getElementById('typed');
if (typedEl) {
  const phrases = [
    'Maker, tinkerer, always mid-project.',
    'Building tools, gadgets, and things I couldn\'t find for sale.',
    'At the bench, in the water, or somewhere in between.'
  ];
  const reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (reduceMotion) {
    typedEl.textContent = phrases[0];
  } else {
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
}

// Project filter
const filterBtns = document.querySelectorAll('.filter-btn');
const projectCards = document.querySelectorAll('.project-card[data-tags]');
if (filterBtns.length && projectCards.length) {
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      projectCards.forEach(card => {
        const show = filter === 'all' || card.dataset.tags.split(' ').includes(filter);
        card.style.display = show ? '' : 'none';
      });
    });
  });
}

const reduceMotion = window.matchMedia &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

document.querySelectorAll('[data-crack]').forEach(root => {
  const range = root.querySelector('input[type="range"]');
  const setSplit = (value) => {
    const next = Math.max(0, Math.min(100, value));
    root.style.setProperty('--split', next + '%');
    range.value = String(next);
  };
  range.addEventListener('input', () => setSplit(Number(range.value)));
  if (!reduceMotion) {
    root.addEventListener('pointermove', (event) => {
      if (event.pointerType !== 'mouse') return;
      const box = root.getBoundingClientRect();
      setSplit((event.clientX - box.left) / box.width * 100);
    });
  }
});

document.querySelectorAll('video[data-clip]').forEach(video => {
  if (reduceMotion) return;
  const start = () => video.play().catch(() => {});
  if ('IntersectionObserver' in window) {
    const watch = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) start();
        else video.pause();
      });
    }, { threshold: 0.35 });
    watch.observe(video);
  } else {
    start();
  }
});
