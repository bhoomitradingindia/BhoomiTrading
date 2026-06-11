/**
 * Bhoomi Trading – main.js
 * Handles: scroll-based fade-in, sticky nav, mobile menu
 */

/* ─── Scroll-triggered fade-in ────────────────────────────
   Elements with class .fade-up become visible when they
   enter the viewport (plus a small margin so they animate
   just before they're fully visible).
──────────────────────────────────────────────────────────── */
(function initFadeObserver() {
  const elements = document.querySelectorAll('.fade-up');
  if (!elements.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target); // animate once only
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );

  elements.forEach(el => observer.observe(el));
})();


/* ─── Sticky navbar shadow on scroll ───────────────────── */
(function initNavScroll() {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  const onScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll(); // run once on load
})();


/* ─── Mobile navigation toggle ─────────────────────────── */
(function initMobileNav() {
  const toggle = document.getElementById('navToggle');
  const links  = document.getElementById('navLinks');
  if (!toggle || !links) return;

  toggle.addEventListener('click', () => {
    const isOpen = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', isOpen);
    // Prevent body scroll when menu is open
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  // Close menu when a link is clicked
  links.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      links.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  // Close menu on ESC
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && links.classList.contains('open')) {
      links.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      toggle.focus();
    }
  });
})();


/* ─── Active nav link highlight on scroll (single-page) ── */
// Not needed for multi-page Flask app — handled server-side via
// the Jinja2 active class in base.html. Kept as a no-op stub
// in case the project later uses anchor-based navigation.


/* ─── Keyboard accessibility for catalogue cards ─────────
   Allow ENTER / SPACE to trigger toggleCategory on the button.
   (Handled natively since .cat-card__header is a <button>.)
──────────────────────────────────────────────────────────── */


/* ─── Smooth hash scroll with nav offset ─────────────────
   When following an anchor link (#rexine etc.) offset the
   scroll position so the fixed navbar doesn't cover the target.
──────────────────────────────────────────────────────────── */
(function initHashScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const id = this.getAttribute('href').slice(1);
      const target = document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      const navH = parseInt(
        getComputedStyle(document.documentElement).getPropertyValue('--nav-h'),
        10
      ) || 72;
      const top = target.getBoundingClientRect().top + window.scrollY - navH - 16;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });
})();


function toggleSubtypes(id) {
  const box = document.getElementById("subtypes-" + id);
  box.classList.toggle("show");
}

function filterMaterials() {
  const searchValue = document.getElementById("searchInput").value.toLowerCase();
  const categoryValue = document.getElementById("categoryFilter").value;
  const cards = document.querySelectorAll(".material-card-box");

  cards.forEach(card => {
    const name = card.getAttribute("data-name");
    const category = card.getAttribute("data-category");

    const matchSearch = name.includes(searchValue);
    const matchCategory = categoryValue === "all" || category === categoryValue;

    if (matchSearch && matchCategory) {
      card.style.display = "block";
    } else {
      card.style.display = "none";
    }
  });
}

const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    navLinks.classList.toggle("active");
  });

  const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    navLinks.classList.toggle("open");
  });
}

}