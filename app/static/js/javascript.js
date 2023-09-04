// CLEAR BUTTON

document.querySelector('.clear-button').addEventListener('click', function () {
  document.querySelector('.search-field').value = '';
});

const searchInput = document.querySelector('.search-field');
const clearButton = document.querySelector('.clear-button');

searchInput.addEventListener('input', function () {
  clearButton.style.display = this.value ? 'block' : 'none';
});

clearButton.addEventListener('click', function () {
  searchInput.value = '';
  clearButton.style.display = 'none';
});


// EMPTY STATE

document.addEventListener("DOMContentLoaded", function () {
  const clickableResults = document.querySelectorAll('.search-result-item-link');

  clickableResults.forEach(function (element) {
    element.addEventListener('click', function () {
      // Hide results and show loading animation
      document.getElementById("results").style.display = "none";
      document.getElementById("loading").style.display = "block";
    });
  });
});