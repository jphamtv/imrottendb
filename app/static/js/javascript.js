// CLEAR BUTTON

// Function to toggle the clear button based on search input
function toggleClearButton() {
  const searchInput = document.querySelector('.search-field');
  const clearButton = document.querySelector('.clear-button');
  clearButton.style.display = searchInput.value ? 'block' : 'none';
}

// Listen for the DOMContentLoaded event then toggle the clear button
document.addEventListener('DOMContentLoaded', function() {
  toggleClearButton();
});

// Listen for input on search field then toggle the clear button
document.querySelector('.search-field').addEventListener('input', function () {
  toggleClearButton();
});

// Listen for clicks on the clear button to clear the search field
document.querySelector('.clear-button').addEventListener('click', function () {
  document.querySelector('.search-field').value = '';
  toggleClearButton();
  searchInput.focus();
});