// Animation JavaScript for CubeDodge

// Scroll reveal animation
function revealOnScroll() {
    const elements = document.querySelectorAll('.reveal');
    
    elements.forEach(element => {
        // Get the element's position relative to the viewport
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150; // How many pixels from the top before the element becomes visible
        
        if (elementTop < window.innerHeight - elementVisible) {
            element.classList.add('active');
        } else {
            element.classList.remove('active');
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add reveal class to elements we want to animate on scroll
    const sections = document.querySelectorAll('.latest-news, .contact-section');
    sections.forEach(section => {
        section.classList.add('reveal');
    });
    
    const newsItems = document.querySelectorAll('.news-item');
    newsItems.forEach(item => {
        item.classList.add('reveal');
    });
    
    // Check position on initial load
    revealOnScroll();
    
    // Listen for scroll events
    window.addEventListener('scroll', revealOnScroll);
    
    // Add particle background to hero section (optional)
    setupParticles();
});

// Optional: Add subtle particle background to hero section
function setupParticles() {
    const hero = document.querySelector('.hero');
    
    // Create canvas element if it doesn't interfere with your video background
    // Only add if there's no video background or if the video isn't loading
    const videoElement = document.querySelector('.background-video');
    if (!videoElement || videoElement.error) {
        const canvas = document.createElement('canvas');
        canvas.className = 'particle-canvas';
        canvas.style.position = 'absolute';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '-1';
        
        hero.appendChild(canvas);
        
        // Setup canvas and particles
        const ctx = canvas.getContext('2d');
        const particles = [];
        
        function resizeCanvas() {
            canvas.width = hero.offsetWidth;
            canvas.height = hero.offsetHeight;
        }
        
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
        
        // Create particles
        for (let i = 0; i < 50; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 2 + 1,
                color: 'rgba(255, 255, 255, 0.5)',
                speed: Math.random() * 0.5 + 0.1,
                direction: Math.random() * Math.PI * 2
            });
        }
        
        // Animation loop
        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            particles.forEach(particle => {
                // Move particles
                particle.x += Math.cos(particle.direction) * particle.speed;
                particle.y += Math.sin(particle.direction) * particle.speed;
                
                // Wrap around screen
                if (particle.x < 0) particle.x = canvas.width;
                if (particle.x > canvas.width) particle.x = 0;
                if (particle.y < 0) particle.y = canvas.height;
                if (particle.y > canvas.height) particle.y = 0;
                
                // Draw particle
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
                ctx.fillStyle = particle.color;
                ctx.fill();
            });
            
            requestAnimationFrame(animateParticles);
        }
        
        animateParticles();
    }
}

// Add a subtle loading animation
window.addEventListener('load', function() {
    document.body.classList.add('page-loaded');
});