/* ==========================================================================
   UFR STA — Script principal
   Gère l'ouverture/fermeture du menu mobile (nav-toggle / main-nav)
   À inclure sur TOUTES les pages, juste avant </body>
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.querySelector('.nav-toggle');
  const mainNav = document.querySelector('.main-nav');

  if (!navToggle || !mainNav) return;

  const closeMenu = () => {
    mainNav.classList.remove('open');
    navToggle.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Ouvrir le menu');
  };

  const openMenu = () => {
    mainNav.classList.add('open');
    navToggle.classList.add('open');
    navToggle.setAttribute('aria-expanded', 'true');
    navToggle.setAttribute('aria-label', 'Fermer le menu');
  };

  // Clic sur le bouton hamburger
  navToggle.addEventListener('click', () => {
    const isOpen = mainNav.classList.contains('open');
    isOpen ? closeMenu() : openMenu();
  });

  // Ferme le menu quand on clique un lien de navigation (mobile)
  mainNav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', closeMenu);
  });

  // Ferme le menu si on clique en dehors de la nav (mobile)
  document.addEventListener('click', (e) => {
    const clickedInsideNav = mainNav.contains(e.target);
    const clickedToggle = navToggle.contains(e.target);
    if (!clickedInsideNav && !clickedToggle && mainNav.classList.contains('open')) {
      closeMenu();
    }
  });

  // Ferme le menu automatiquement si on repasse en desktop
  window.addEventListener('resize', () => {
    if (window.innerWidth > 720 && mainNav.classList.contains('open')) {
      closeMenu();
    }
  });

  // Ferme le menu avec la touche Échap
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mainNav.classList.contains('open')) {
      closeMenu();
    }
  });
});

let albumCourant = 0;
let photoCourante = 0;

function ouvrirAlbum(indexAlbum, indexPhoto = 0) {
  albumCourant = indexAlbum;
  photoCourante = indexPhoto;
  afficherPhoto();
  document.getElementById('lightbox').hidden = false;
  document.body.style.overflow = 'hidden';
}

function fermerLightbox() {
  document.getElementById('lightbox').hidden = true;
  document.body.style.overflow = '';
}

function afficherPhoto() {
  const album = albumsData[albumCourant];
  const img = document.getElementById('lightbox-image');
  img.src = album.photos[photoCourante];
  img.alt = album.titre + ' — photo ' + (photoCourante + 1);
  document.getElementById('lightbox-titre').textContent = album.titre;
  document.getElementById('lightbox-compteur').textContent =
    (photoCourante + 1) + ' / ' + album.photos.length;
}

function photoSuivante() {
  const album = albumsData[albumCourant];
  photoCourante = (photoCourante + 1) % album.photos.length;
  afficherPhoto();
}

function photoPrecedente() {
  const album = albumsData[albumCourant];
  photoCourante = (photoCourante - 1 + album.photos.length) % album.photos.length;
  afficherPhoto();
}

document.addEventListener('keydown', (e) => {
  const lightbox = document.getElementById('lightbox');
  if (!lightbox || lightbox.hidden) return;
  if (e.key === 'Escape') fermerLightbox();
  if (e.key === 'ArrowRight') photoSuivante();
  if (e.key === 'ArrowLeft') photoPrecedente();
});

document.addEventListener('DOMContentLoaded', () => {
  const lightbox = document.getElementById('lightbox');
  if (!lightbox) return; // Cette page n'a pas de galerie, on ne fait rien
  // Ferme si on clique en dehors de l'image
  lightbox.addEventListener('click', (e) => {
    if (e.target.id === 'lightbox') fermerLightbox();
  });
});