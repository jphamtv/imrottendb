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
});


// document.addEventListener("DOMContentLoaded", function() {
//   // Initialize search input and clear button
//   const searchInput = document.querySelector('.search-field');
//   const clearButton = document.querySelector('.clear-button');

//   // Check initial value of the search input field
//   if (searchInput.value) {
//     clearButton.style.display = 'block';
//   }

//   // Listen to input changes
//   searchInput.addEventListener('input', function () {
//     clearButton.style.display = this.value ? 'block' : 'none';
//   });

//   // Clear input when the clear button is clicked
//   clearButton.addEventListener('click', function () {
//     searchInput.value = '';
//     clearButton.style.display = 'none';
//   });
// });


// document.querySelector('.clear-button').addEventListener('click', function () {
//   document.querySelector('.search-field').value = '';
// });

// const searchInput = document.querySelector('.search-field');
// const clearButton = document.querySelector('.clear-button');

// searchInput.addEventListener('input', function () {
//   clearButton.style.display = this.value ? 'block' : 'none';
// });

// clearButton.addEventListener('click', function () {
//   searchInput.value = '';
//   clearButton.style.display = 'none';
// });


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