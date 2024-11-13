// Ensure that dropdown menus are hidden by default when the page loads
document.querySelectorAll('.dropdown-content').forEach(dropdown => {
  dropdown.style.display = 'none';  // Set all dropdowns to be hidden initially
});

// Toggle dropdown menu when a menu icon is clicked
document.querySelectorAll('.menu-toggle').forEach(menuToggle => {
  menuToggle.addEventListener('click', function(event) {
    // Prevent the event from bubbling up
    event.stopPropagation();

    // Find the closest dropdown-content to this specific menu toggle
    const dropdown = menuToggle.nextElementSibling;

    // Toggle the visibility of the dropdown menu
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
  });
});

// Close all dropdowns if clicked outside
document.addEventListener('click', function(event) {
  document.querySelectorAll('.dropdown-content').forEach(dropdown => {
    // Check if the click was outside any dropdown or menu-toggle
    if (!dropdown.contains(event.target) && !event.target.closest('.menu-toggle')) {
      dropdown.style.display = 'none';  // Hide the dropdown if clicked outside
    }
  });
});

document.addEventListener('DOMContentLoaded', function () {
    const likeIcons = document.querySelectorAll('.like-button i');

    likeIcons.forEach(function (icon) {
        icon.addEventListener('click', function () {
            const likeButton = this.closest('.like-button');
            const postId = likeButton.getAttribute('data-post-id');
            const isLiked = this.classList.contains('fa-solid');

            // Send the AJAX request to like/unlike the post
            fetch(`/like/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ post_id: postId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the like count
                    const likeCountElement = likeButton.querySelector('.like-count');
                    likeCountElement.textContent = data.new_like_count;

                    // Toggle the heart icon color
                    if (isLiked) {
                        this.classList.remove('fa-solid');
                        this.classList.add('fa-regular');
                        this.style.color = ''; // Reset color (white)
                    } else {
                        this.classList.remove('fa-regular');
                        this.classList.add('fa-solid');
                        this.style.color = 'red'; // Fill with red when liked
                    }
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});

// comment box //
 // Toggle visibility of the comment box when the comment icon is clicked
document.querySelectorAll('.commentIcon').forEach(menuToggle => {
  menuToggle.addEventListener('click', function(event) {
    // Prevent the event from bubbling up (we don't want this to close other dropdowns)
    event.stopPropagation();

    // Find the closest comment box to this specific menu toggle
    const commentBox = menuToggle.nextElementSibling;

    // Toggle the visibility of the comment box
    commentBox.style.display = commentBox.style.display === 'block' ? 'none' : 'block';
  });
});

// Close all comment boxes if clicked outside
document.addEventListener('click', function(event) {
  document.querySelectorAll('.commentBox').forEach(commentBox => {
    // Check if the click was outside any comment box or menu-toggle
    if (!commentBox.contains(event.target) && !event.target.closest('.commentIcon')) {
      commentBox.style.display = 'none';  // Hide the comment box if clicked outside
    }
  });
});

