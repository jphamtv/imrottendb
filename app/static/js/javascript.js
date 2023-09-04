// CLEAR BUTTON

document.querySelector('.clear-button').addEventListener('click', function () {
  document.querySelector('.search-field').value = '';
});

const searchInput = document.querySelector('.search-field');
const clearButton = document.querySelector('.clear-button');

searchInput.addEventListener('input', function() {
  clearButton.style.display = this.value ? 'block' : 'none';
});

clearButton.addEventListener('click', function() {
  searchInput.value = '';
  clearButton.style.display = 'none';
});


