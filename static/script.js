document.addEventListener("DOMContentLoaded", () => {
    // Validate Add Author Form
    const addAuthorForm = document.querySelector("form[action='/add_author']");
    if (addAuthorForm) {
        addAuthorForm.addEventListener("submit", (event) => {
            const nameInput = document.getElementById("name");
            const birthDateInput = document.getElementById("birth_date");
            const deathDateInput = document.getElementById("date_of_death");

            // Ensure the name is not empty
            if (!nameInput.value.trim()) {
                event.preventDefault();
                alert("Author name is required!");
                return;
            }

            // Ensure birth date is before date of death (if provided)
            if (birthDateInput.value && deathDateInput.value && new Date(birthDateInput.value) > new Date(deathDateInput.value)) {
                event.preventDefault();
                alert("Birthdate must be before the date of death!");
            }
        });
    }

    // Validate Add Book Form
    const addBookForm = document.querySelector("form[action='/add_book']");
    if (addBookForm) {
        addBookForm.addEventListener("submit", (event) => {
            const isbnInput = document.getElementById("isbn");
            const titleInput = document.getElementById("title");
            const publicationYearInput = document.getElementById("publication_year");
            const authorSelect = document.getElementById("author_id");

            // Validate ISBN
            const isbnValue = isbnInput.value.trim();
            if (!/^\d{10}(\d{3})?$/.test(isbnValue)) {
                event.preventDefault();
                alert("ISBN must be 10 or 13 digits!");
                return;
            }

            // Validate title
            if (!titleInput.value.trim()) {
                event.preventDefault();
                alert("Book title is required!");
                return;
            }

            // Validate publication year (optional check if needed)
            if (publicationYearInput.value && isNaN(publicationYearInput.value)) {
                event.preventDefault();
                alert("Please enter a valid year for the publication year!");
                return;
            }

            // Validate author selection
            if (!authorSelect.value) {
                event.preventDefault();
                alert("Please select an author!");
            }
        });
    }

    // Add confirmation prompt for delete buttons
    const deleteButtons = document.querySelectorAll("form[action^='/book/'][method='POST'] button");
    deleteButtons.forEach(button => {
        button.addEventListener("click", (event) => {
            if (!confirm("Are you sure you want to delete this book? This action cannot be undone.")) {
                event.preventDefault();
            }
        });
    });

    // Scroll functionality for book list
    const scrollLeftButton = document.querySelector(".scroll-button.left");
    const scrollRightButton = document.querySelector(".scroll-button.right");
    const bookGrid = document.querySelector(".book-grid");
    const scrollContainer = document.querySelector(".book-grid");

    const bookWidth = document.querySelector(".book-card").offsetWidth;
    const gap = 20;

    const scrollStep = (bookWidth + gap) * 4;

    if (scrollLeftButton && scrollRightButton && bookGrid) {
        scrollLeftButton.addEventListener("click", () => {
            bookGrid.scrollBy({
                left: -scrollStep,
                behavior: "smooth",
            });
        });

        scrollRightButton.addEventListener("click", () => {
            bookGrid.scrollBy({
                left: scrollStep,
                behavior: "smooth",
            });
        });
    }

    const searchInput = document.getElementById("search");
    if (searchInput) {
        searchInput.value = ""; // Clear the input field on page load
    }
});
