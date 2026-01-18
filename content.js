function hideSendToTeacherButton() {
  const buttons = document.querySelectorAll('button');
  buttons.forEach(button => {
    if (button.textContent.trim() === 'Send to teacher') {
      button.style.display = 'none';
    }
  });
}

// Run once DOM is ready
document.addEventListener('DOMContentLoaded', hideSendToTeacherButton);

// Also observe for dynamic changes
const observer = new MutationObserver(hideSendToTeacherButton);
observer.observe(document.body, { childList: true, subtree: true });
