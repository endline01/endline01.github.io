/* ===========================================================================
   Osama Hussein — Portfolio interactions
   Theme toggle (+ system preference), mobile nav drawer, scroll-spy,
   app-bar elevation on scroll, and staggered reveal-on-scroll.
   =========================================================================== */
(function () {
  "use strict";

  var root = document.documentElement;

  /* ── Theme toggle ─────────────────────────────────────────────────────────
     No [data-theme] attribute  → follow the OS (prefers-color-scheme).
     Explicit attribute         → forced light/dark, persisted to localStorage.
     The toggle reflects whichever theme is *currently effective*. */
  var toggle = document.getElementById("themeToggle");
  var sun = toggle.querySelector(".icon-sun");
  var moon = toggle.querySelector(".icon-moon");
  var media = window.matchMedia("(prefers-color-scheme: dark)");

  function effectiveTheme() {
    var attr = root.getAttribute("data-theme");
    if (attr === "light" || attr === "dark") return attr;
    return media.matches ? "dark" : "light";
  }

  function syncToggle() {
    var dark = effectiveTheme() === "dark";
    sun.style.display = dark ? "none" : "block";
    moon.style.display = dark ? "block" : "none";
    toggle.setAttribute("aria-pressed", String(dark));
    toggle.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
  }

  toggle.addEventListener("click", function () {
    var next = effectiveTheme() === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("theme", next); } catch (e) {}
    syncToggle();
  });

  // If the user hasn't made an explicit choice, react to OS changes live.
  media.addEventListener("change", function () {
    if (!root.getAttribute("data-theme")) syncToggle();
  });

  syncToggle();

  /* ── Mobile navigation drawer ─────────────────────────────────────────────*/
  var navToggle = document.getElementById("navToggle");
  var navClose = document.getElementById("navClose");
  var navScrim = document.getElementById("navScrim");
  var navDrawer = document.getElementById("navDrawer");

  function openNav() {
    document.body.setAttribute("data-nav-open", "true");
    navScrim.hidden = false;
    navToggle.setAttribute("aria-expanded", "true");
    navDrawer.setAttribute("aria-hidden", "false");
    navClose.focus();
  }
  function closeNav() {
    document.body.removeAttribute("data-nav-open");
    navToggle.setAttribute("aria-expanded", "false");
    navDrawer.setAttribute("aria-hidden", "true");
    // Keep scrim in the DOM during the transition, then hide it.
    window.setTimeout(function () {
      if (!document.body.hasAttribute("data-nav-open")) navScrim.hidden = true;
    }, 300);
  }

  navToggle.addEventListener("click", openNav);
  navClose.addEventListener("click", closeNav);
  navScrim.addEventListener("click", closeNav);
  navDrawer.addEventListener("click", function (e) {
    if (e.target.closest("a")) closeNav();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && document.body.hasAttribute("data-nav-open")) {
      closeNav();
      navToggle.focus();
    }
  });

  /* ── App-bar elevation on scroll ──────────────────────────────────────────*/
  var appBar = document.getElementById("appBar");
  function onScroll() {
    appBar.setAttribute("data-scrolled", window.scrollY > 8 ? "true" : "false");
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ── Scroll-spy: highlight the active section in the nav ───────────────────*/
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav__link"));
  var linkFor = {};
  navLinks.forEach(function (link) {
    var id = link.getAttribute("href").slice(1);
    linkFor[id] = link;
  });

  // Map every observed section to the nav link that represents it.
  var sectionToLink = {
    about: "about", experience: "experience",
    skills: "skills", tools: "skills",
    projects: "projects",
    education: "credentials", credentials: "credentials",
    contact: "contact"
  };
  var observed = Object.keys(sectionToLink)
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);

  function setActive(navId) {
    navLinks.forEach(function (l) { l.removeAttribute("aria-current"); });
    if (linkFor[navId]) linkFor[navId].setAttribute("aria-current", "true");
  }

  if ("IntersectionObserver" in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var navId = sectionToLink[entry.target.id];
          if (navId) setActive(navId);
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px", threshold: 0 });
    observed.forEach(function (s) { spy.observe(s); });
  }

  /* ── Reveal on scroll (staggered) ─────────────────────────────────────────*/
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var revealEls = Array.prototype.slice.call(document.querySelectorAll(".reveal"));

  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  } else {
    var revealer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        // Stagger siblings that enter together for a calm cascade.
        var siblings = Array.prototype.slice.call(
          el.parentElement.querySelectorAll(":scope > .reveal")
        );
        var idx = Math.max(0, siblings.indexOf(el));
        el.style.transitionDelay = Math.min(idx * 70, 350) + "ms";
        el.classList.add("is-visible");
        obs.unobserve(el);
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.08 });
    revealEls.forEach(function (el) { revealer.observe(el); });
  }

  /* ── Footer year ──────────────────────────────────────────────────────────*/
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* ── Background video: pause under reduced-motion to save resources ────────*/
  (function bgVideo() {
    var v = document.querySelector(".bg-fx__video");
    if (!v) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      v.removeAttribute("autoplay"); v.pause();
    }
  })();

  /* ── Hero name: one-time "decode" / text-scramble on load ─────────────────*/
  (function decodeName() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var el = document.getElementById("heroName");
    if (!el) return;
    var final = el.getAttribute("data-text") || el.textContent;
    var pool = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&/<>*".split("");
    var reveal = 0;
    var tick = setInterval(function () {
      var out = "";
      for (var i = 0; i < final.length; i++) {
        if (final[i] === " ") { out += " "; continue; }
        out += i < Math.floor(reveal) ? final[i] : pool[(Math.random() * pool.length) | 0];
      }
      el.textContent = out;
      reveal += 1.1;
      if (reveal >= final.length) { el.textContent = final; clearInterval(tick); }
    }, 38);
  })();
})();
