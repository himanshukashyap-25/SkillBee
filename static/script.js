document.addEventListener('DOMContentLoaded', function () {

  // 1) Scroll fade-in animation for all cards
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animation = "fadeInUp 0.8s ease forwards";
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.card').forEach((card, i) => {
    card.style.animationDelay = `${i * 0.1}s`;
    observer.observe(card);
  });

  // 2) Custom modal functionality for "skillModal" (home/learn skill cards)
  const skillModalEl = document.getElementById('skillModal');
  if (skillModalEl) {
    const skillModalCloseBtn = skillModalEl.querySelector('.close');
    const skillModalTitle = skillModalEl.querySelector('#modalTitle');
    const skillModalDesc = skillModalEl.querySelector('#modalDesc');
    const skillModalVideo = skillModalEl.querySelector('#modalVideo'); // optional <video> element

    const openSkillModal = (title, desc, videoSrc) => {
      if (skillModalTitle) skillModalTitle.textContent = title || '';
      if (skillModalDesc) skillModalDesc.textContent = desc || '';
      if (skillModalVideo) {
        if (videoSrc) {
          skillModalVideo.src = videoSrc;
          skillModalVideo.style.display = 'block';
        } else {
          skillModalVideo.pause && skillModalVideo.pause();
          skillModalVideo.src = '';
          skillModalVideo.style.display = 'none';
        }
      }
      skillModalEl.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    };

    const closeSkillModal = () => {
      skillModalEl.style.display = 'none';
      if (skillModalVideo) {
        try { skillModalVideo.pause(); } catch (e) {}
        skillModalVideo.src = '';
        skillModalVideo.style.display = 'none';
      }
      document.body.style.overflow = '';
    };

    document.querySelectorAll('.skill-card').forEach(card => {
      card.addEventListener('click', () => {
        const title = card.dataset.skill || (card.querySelector('h4')?.innerText) || '';
        const desc = card.dataset.desc || (card.querySelector('p')?.innerText) || '';
        const videoSrc = card.dataset.video || ''; // optional data-video attribute
        openSkillModal(title, desc, videoSrc);
      });
    });

    skillModalCloseBtn?.addEventListener('click', closeSkillModal);
    window.addEventListener('click', (e) => { if (e.target === skillModalEl) closeSkillModal(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && skillModalEl.style.display === 'flex') closeSkillModal(); });
  }

  // 3) Upload form functionality for Teach page (new code)
  const teachForm = document.getElementById('teachForm');
  const successModal = document.getElementById('successModal');
  const closeModalBtn = successModal.querySelector('.close');
  const goToLearnBtn = document.getElementById('goToLearn');

  teachForm.addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(teachForm);

    fetch(teachForm.action, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json()) // Assuming the server responds with JSON
    .then(data => {
      if (data.success) {
        // Show the success modal
        successModal.style.display = 'flex';
        // Update the modal with tutorial title
        document.getElementById('uploadedTitle').textContent = data.title;
      } else {
        alert("There was an issue uploading the tutorial.");
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert("There was an error submitting your tutorial.");
    });
  });

  // Close the modal when the "close" button is clicked
  closeModalBtn.addEventListener('click', function () {
    successModal.style.display = 'none';
  });

  // 4) Bootstrap video modal logic (for Watch Now buttons using data-* attributes)
  const videoModalEl = document.getElementById('videoModal');
  if (videoModalEl) {
    videoModalEl.addEventListener('show.bs.modal', function (event) {
      const triggerButton = event.relatedTarget;
      if (!triggerButton) return;

      const title = triggerButton.getAttribute('data-title') || '';
      const desc  = triggerButton.getAttribute('data-description') || '';
      const video = triggerButton.getAttribute('data-video') || '';

      const videoFrame = document.getElementById('videoFrame'); // iframe inside modal
      const videoTitle = document.getElementById('videoTitle');
      const videoDesc  = document.getElementById('videoDescription');

      if (videoTitle) videoTitle.textContent = title;
      if (videoDesc) videoDesc.textContent = desc;

      if (videoFrame) {
        // Convert common youtube links to embed format if needed
        let src = video;
        if (video.includes('youtube.com/watch')) {
          src = video.replace('watch?v=', 'embed/');
        } else if (video.includes('youtu.be/')) {
          src = video.replace('youtu.be/', 'www.youtube.com/embed/');
        }
        // If the developer provided a full embed URL already, it will be used as-is
        videoFrame.src = src;
      }
    });

    videoModalEl.addEventListener('hidden.bs.modal', function () {
      const videoFrame = document.getElementById('videoFrame');
      if (videoFrame) videoFrame.src = '';
    });
  }

  // 5) Fetch tutorials and dynamically display them in the Learn section (hardcoded)
  document.addEventListener("DOMContentLoaded", function () {
    // Hardcoded tutorial data (replace this with actual dynamic data from a server)
    const tutorials = [
      { title: "Web Development Bootcamp", description: "Learn full-stack development from scratch!", category: "Software & Tech", level: "Beginner", location: "Online", videoPath: "uploads/webdev.mp4" },
      { title: "Data Science Fundamentals", description: "Master Python, Pandas, and data visualization.", category: "AI / ML", level: "Intermediate", location: "Online", videoPath: "uploads/datasci.mp4" },
      { title: "UI/UX Design Essentials", description: "Design beautiful interfaces with Figma.", category: "Design", level: "Advanced", location: "Remote", videoPath: "uploads/uiux.mp4" },
    ];

    const tutorialsContainer = document.getElementById("tutorialsContainer");
    const categoryFilters = document.getElementById("categoryFilters");
    const searchInput = document.getElementById("searchInput");
    const levelSelect = document.getElementById("levelSelect");
    const locationInput = document.getElementById("locationInput");
    const searchBtn = document.getElementById("searchBtn");

    // Function to display tutorials
    function displayTutorials(filteredTutorials) {
      tutorialsContainer.innerHTML = "";
      filteredTutorials.forEach(tutorial => {
        const card = document.createElement("div");
        card.classList.add("col-md-4");
        card.innerHTML = `
          <div class="card skill-card p-4" data-category="${tutorial.category}" data-level="${tutorial.level}" data-location="${tutorial.location}">
            <h4>${tutorial.title}</h4>
            <p>${tutorial.description}</p>
            <button class="btn btn-warning mt-2">Explore</button>
          </div>
        `;
        tutorialsContainer.appendChild(card);
      });
    }

    // Display tutorials initially
    displayTutorials(tutorials);

    // Search functionality
    searchBtn.addEventListener("click", () => {
      const query = searchInput.value.toLowerCase();
      const level = levelSelect.value;
      const location = locationInput.value.toLowerCase();

      const filteredTutorials = tutorials.filter(tutorial => {
        return (
          (tutorial.title.toLowerCase().includes(query) || tutorial.description.toLowerCase().includes(query)) &&
          (level === "Select level" || tutorial.level === level) &&
          (location === "" || tutorial.location.toLowerCase().includes(location))
        );
      });

      displayTutorials(filteredTutorials);
    });

    // Filter tutorials by category
    function filterTutorials(filters) {
      const filteredTutorials = tutorials.filter(tutorial => {
        return (
          (!filters.category || tutorial.category === filters.category)
        );
      });
      displayTutorials(filteredTutorials);
    }

    // Dynamically generate category filters
    const categories = Array.from(new Set(tutorials.map(t => t.category)));
    categories.forEach(category => {
      const button = document.createElement("button");
      button.textContent = category;
      button.classList.add("filter-btn");
      button.addEventListener("click", () => {
        filterTutorials({ category });
      });
      categoryFilters.appendChild(button);
    });
  });

  // 6) Join Modal Functionality
  const modal = document.getElementById("joinModal");
  const joinBtn = document.getElementById("joinBtn");
  const closeBtn = modal ? modal.querySelector(".join-close") : null;

  if (joinBtn && modal && closeBtn) {
    joinBtn.addEventListener("click", () => {
      modal.style.display = "flex";
    });

    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });

    window.addEventListener("click", (event) => {
      if (event.target === modal) {
        modal.style.display = "none";
      }
    });
  } else {
    console.error("Join button or modal not found in DOM.");
  }

  // 7) Enroll Button (for skill modal)
  const skillEnrollBtn = document.getElementById("modalEnrollBtn");
  skillEnrollBtn?.addEventListener("click", () => {
    alert("✅ You have successfully enrolled in this skill!");
    document.getElementById("skillModal").style.display = "none";
  });

});
document.addEventListener('DOMContentLoaded', function () {
  // 1) Upload form functionality for Teach page
  const teachForm = document.getElementById('teachForm');
  const successModal = document.getElementById('successModal');
  const closeModalBtn = successModal.querySelector('.close');
  const goToLearnBtn = document.getElementById('goToLearn');

  teachForm.addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(teachForm);

    fetch(teachForm.action, {
      method: 'POST',
      body: formData
    })
    .then(response => response.json()) // Assuming the server responds with JSON
    .then(data => {
      if (data.success) {
        // Show the success modal
        successModal.style.display = 'flex';
        // Update the modal with tutorial title
        document.getElementById('uploadedTitle').textContent = data.title;
      } else {
        alert("There was an issue uploading the tutorial.");
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert("There was an error submitting your tutorial.");
    });
  });

  // Close the modal when the "close" button is clicked
  closeModalBtn.addEventListener('click', function () {
    successModal.style.display = 'none';
  });

  // 4) Redirect to Learn Page
  goToLearnBtn.addEventListener('click', function () {
    window.location.href = 'learn.html';
  });
  // For Join Now form
document.getElementById('joinForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const response = await fetch('/join', { method: 'POST', body: formData });
  const result = await response.json();
  alert(result.message);
});

// For search suggestions
document.getElementById('searchInput').addEventListener('input', async (e) => {
  const query = e.target.value;
  if (query.length > 1) {
    const response = await fetch(`/api/search?q=${query}`);
    const suggestions = await response.json();
    // Populate #suggestionList with suggestions
  }
});

// For modals (e.g., skill modal)
document.querySelectorAll('.skill-card button').forEach(btn => {
  btn.addEventListener('click', async () => {
    const skillId = btn.dataset.skillId;  // Add data-skill-id to buttons
    const response = await fetch(`/api/skill/${skillId}`);
    const data = await response.json();
    // Populate modal with data
  });
});

// Similar for tutorials and enroll

});
const form = document.querySelector('form');  // agar form unique hai to
const resultsContainer = document.getElementById('search-results');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const query = document.querySelector('input[name="query"]').value;
  const level = document.querySelector('select[name="level"]').value;
  const location = document.querySelector('input[name="location"]').value;

  const response = await fetch(`/search?query=${encodeURIComponent(query)}&level=${encodeURIComponent(level)}&location=${encodeURIComponent(location)}`);
  const courses = await response.json();

  resultsContainer.innerHTML = '';

  if (courses.length === 0) {
    resultsContainer.textContent = 'Koi course nahi mila aapke criteria se.';
    return;
  }

  courses.forEach(course => {
    const div = document.createElement('div');
    div.classList.add('course-card');
    div.innerHTML = `
      <h3>${course.course_name}</h3>
      <p><strong>Skills:</strong> ${course.skills.join(', ')}</p>
      <p><strong>Level:</strong> ${course.level}</p>
      <p><strong>Location:</strong> ${course.location}</p>
      <p><strong>Mentor:</strong> ${course.mentor}</p>
      <p>${course.description}</p>
    `;
    resultsContainer.appendChild(div);
  });
});
