/* DAS GmbH – site.js (no dependencies) */
(function () {
  "use strict";
  var d = document;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };

  /* ---- Nav: scrolled state via sentinel ---- */
  var nav = $(".nav");
  var sentinel = $("#top-sentinel");
  if (nav && sentinel && "IntersectionObserver" in window) {
    new IntersectionObserver(function (e) {
      nav.classList.toggle("is-scrolled", !e[0].isIntersecting);
    }).observe(sentinel);
  }

  /* ---- Burger / overlay menu ---- */
  var burger = $(".burger");
  var menu = $("#menu");
  function setMenu(open) {
    if (!nav || !burger) return;
    nav.classList.toggle("is-open", open);
    d.body.classList.toggle("menu-open", open);
    burger.setAttribute("aria-expanded", open ? "true" : "false");
    burger.setAttribute("aria-label", open ? "Menü schließen" : "Menü öffnen");
    if (menu) menu.setAttribute("aria-hidden", open ? "false" : "true");
    if (menu) { if (open) menu.removeAttribute("inert"); else menu.setAttribute("inert", ""); }
  }
  if (burger) {
    burger.addEventListener("click", function () { setMenu(!nav.classList.contains("is-open")); });
    $$("#menu a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    d.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  }

  /* ---- Promo slider ---- */
  $$("[data-slider]").forEach(function (root) {
    var slides = $$(".slide", root), dots = $$(".dots button", root), i = 0, t = null;
    function go(n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) {
        var on = k === i;
        s.classList.toggle("is-active", on);
        s.setAttribute("aria-hidden", on ? "false" : "true");
        if (on) s.removeAttribute("inert"); else s.setAttribute("inert", "");
      });
      dots.forEach(function (b, k) { b.setAttribute("aria-current", k === i ? "true" : "false"); });
    }
    function play() { stop(); if (!reduce) t = setInterval(function () { go(i + 1); }, 6000); }
    function stop() { if (t) clearInterval(t); t = null; }
    dots.forEach(function (b, k) { b.addEventListener("click", function () { go(k); play(); }); });
    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", play);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", play);
    go(0); play();
  });

  /* ---- Generic collapse toggles (Leistungen "Alle anzeigen") ---- */
  $$("[data-more]").forEach(function (btn) {
    var box = d.getElementById(btn.getAttribute("aria-controls"));
    var label = $(".toggle__l", btn);
    var count = btn.closest(".svc__body") && $(".more-count", btn.closest(".svc__body"));
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") !== "true";
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      box.classList.toggle("is-open", open);
      box.setAttribute("aria-hidden", open ? "false" : "true");
      if (label) label.textContent = open ? "Weniger anzeigen" : "Alle anzeigen";
      if (count) count.hidden = open;
    });
  });

  /* ---- Accordions (FAQ + Jobs) ---- */
  $$("[data-acc]").forEach(function (item) {
    var btn = $("[aria-controls]", item);
    var panel = d.getElementById(btn.getAttribute("aria-controls"));
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") !== "true";
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      item.classList.toggle("is-open", open);
      panel.classList.toggle("is-open", open);
      panel.setAttribute("aria-hidden", open ? "false" : "true");
    });
  });

  /* ---- Interactive car ---- */
  var ia = $("[data-ia]");
  if (ia) {
    var data = JSON.parse($("#ia-data").textContent);
    var card = $(".ia-card", ia);
    var hs = $$(".hs", ia), chips = $$(".chip", ia);
    hs.forEach(function (b) {
      var it = data[b.getAttribute("data-id")];
      b.style.left = it.x + "%";
      b.style.top = it.y + "%";
    });
    var current = "motor";
    function show(id) {
      if (id === current) return;
      current = id;
      var it = data[id];
      hs.forEach(function (b) { b.classList.toggle("is-active", b.getAttribute("data-id") === id); });
      chips.forEach(function (c) { c.setAttribute("aria-selected", c.getAttribute("data-id") === id ? "true" : "false"); c.tabIndex = c.getAttribute("data-id") === id ? 0 : -1; });
      card.classList.add("is-swapping");
      setTimeout(function () {
        $(".ia-t", card).textContent = it.title;
        $(".ia-d", card).textContent = it.description;
        $(".ia-card__ic", card).innerHTML = $("#ic-" + id).innerHTML;
        card.classList.remove("is-swapping");
      }, reduce ? 0 : 260);
    }
    hs.concat(chips).forEach(function (b) { b.addEventListener("click", function () { show(b.getAttribute("data-id")); }); });
    var tl = $("[role=tablist]", ia);
    if (tl) tl.addEventListener("keydown", function (e) {
      var idx = chips.findIndex(function (c) { return c.getAttribute("aria-selected") === "true"; });
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
        e.preventDefault();
        var n = (idx + (e.key === "ArrowRight" ? 1 : -1) + chips.length) % chips.length;
        chips[n].focus(); show(chips[n].getAttribute("data-id"));
      }
    });
  }

  /* ---- Map: load only after click (DSGVO) ---- */
  var mapBtn = $("[data-map]");
  if (mapBtn) {
    mapBtn.addEventListener("click", function () {
      var box = mapBtn.closest(".bezel__core");
      var f = d.createElement("iframe");
      f.src = mapBtn.getAttribute("data-map");
      f.title = "Stuttgart Karte";
      f.loading = "lazy";
      f.referrerPolicy = "no-referrer-when-downgrade";
      f.allowFullscreen = true;
      box.appendChild(f);
      var ph = $(".map__ph", box); if (ph) ph.remove();
    });
  }

  /* ---- Smooth anchor for jobs "Jetzt bewerben" handled by CSS scroll-behavior ---- */

  /* ---- Application form (Readdy form endpoint, as before) ---- */
  var form = $("form[data-endpoint]");
  if (form) {
    var ok = $(".msg--ok", form), err = $(".msg--err", form), errT = $(".msg__t", err);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      ok.classList.remove("is-on"); err.classList.remove("is-on");
      var hp = form.elements.namedItem("website_alt");
      if (hp && hp.value && hp.value.trim()) { ok.classList.add("is-on"); form.reset(); return; }
      var fd = new FormData(form); fd.delete("website_alt");
      var btn = $("[type=submit]", form); btn.disabled = true;
      fetch(form.getAttribute("data-endpoint"), {
        method: "POST",
        body: new URLSearchParams(fd),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      }).then(function (r) {
        return r.text().then(function (txt) {
          var j = null; try { j = JSON.parse(txt); } catch (x) {}
          var m = (j && ((j.meta && (j.meta.message || j.meta.detail)) || j.message)) || txt;
          var spam = m && String(m).toLowerCase().indexOf("spam") > -1;
          if (r.ok && j && j.code === "OK" && !spam) { ok.classList.add("is-on"); form.reset(); }
          else { errT.textContent = m || "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut."; err.classList.add("is-on"); }
        });
      }).catch(function () {
        errT.textContent = "Verbindungsfehler. Bitte versuchen Sie es später erneut.";
        err.classList.add("is-on");
      }).then(function () { btn.disabled = false; });
    });
  }

  /* ---- Scroll reveal ---- */
  if (!reduce && "IntersectionObserver" in window) {
    var vh = window.innerHeight;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    $$(".rv").forEach(function (el) {
      if (el.getBoundingClientRect().top > vh * 0.92) { el.classList.add("pre"); io.observe(el); }
    });
  }
})();
