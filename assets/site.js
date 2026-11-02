// Research page: highlight the sidebar entry for the section being read.
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll(".sections a"));
  var sections = Array.prototype.slice.call(document.querySelectorAll(".listing section[id]"));
  if (!links.length || !sections.length) return;

  function update() {
    var line = window.innerHeight * 0.3;
    var current = sections[0];
    sections.forEach(function (s) {
      if (s.getBoundingClientRect().top <= line) current = s;
    });
    links.forEach(function (a) {
      a.classList.toggle("is-current", a.getAttribute("href") === "#" + current.id);
    });
  }

  var queued = false;
  window.addEventListener("scroll", function () {
    if (queued) return;
    queued = true;
    window.requestAnimationFrame(function () { queued = false; update(); });
  }, { passive: true });
  update();
})();
