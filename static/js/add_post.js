document.addEventListener('DOMContentLoaded', function() {
    const uploadInput = document.getElementById('upload');
    const imagePreview = document.getElementById('imagePreview');
    const nextButton = document.getElementById('nextButton');
    const editSection = document.getElementById('editSection');
    const editedPreview = document.getElementById('editedPreview');
    const filterButtons = document.querySelectorAll('.filter-button');
    const postButton = document.getElementById('postButton');
    const filteredImageInput = document.getElementById('filteredImage');

    let selectedImage = null;
    let currentFilter = 'none';

    // Handle file upload
    uploadInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        const reader = new FileReader();

        reader.onload = function(e) {
            imagePreview.innerHTML = `<img src="${e.target.result}" alt="Uploaded Image">`;
            selectedImage = e.target.result;
            nextButton.style.display = 'block';
        };

        if (file) {
            reader.readAsDataURL(file);
        }
    });

    // Handle next button click
    nextButton.addEventListener('click', function() {
        if (selectedImage) {
            imagePreview.style.display = 'none';
            editedPreview.innerHTML = `<img src="${selectedImage}" alt="Editing Image" style="filter: ${currentFilter};">`;
            editSection.style.display = 'block';
        }
    });

    // Handle filter button clicks
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            currentFilter = this.getAttribute('data-filter');
            const imgElement = editedPreview.querySelector('img');
            if (imgElement) {
                imgElement.style.filter = currentFilter;
            }
        });
    });

    // Handle form submission
    postButton.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default form submission

        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const imgElement = editedPreview.querySelector('img');

            if (!imgElement) {
                console.error("No image found in editedPreview.");
                return;
            }

            if (imgElement.naturalWidth === 0 || imgElement.naturalHeight === 0) {
                console.error("Image dimensions are invalid.");
                return;
            }

            console.log("Image found, applying filter...");

            // Set canvas size
            canvas.width = imgElement.naturalWidth;
            canvas.height = imgElement.naturalHeight;
            ctx.filter = currentFilter;
            ctx.drawImage(imgElement, 0, 0);

            // Convert canvas to data URL
            const filteredImageData = canvas.toDataURL();
            console.log("Filtered Image Data:", filteredImageData);
            filteredImageInput.value = filteredImageData; // Store the filtered image data

            // Submit the form
            const form = document.querySelector('form');
            if (form) {
                form.submit(); // Submit the form
            } else {
                console.error("Form not found.");
            }
        } catch (error) {
            console.error("Image processing failed:", error);
        }
    });
});
