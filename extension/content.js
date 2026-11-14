(() => {
  'use strict';

  const TARGET_BUTTON_TEXT = 'Send to teacher';
  const HIDE_MARK_ATTR = 'data-cbh-hidden';
  const ACTIVE_CLASS = 'cbh-active';
  const STORAGE_KEY = 'enabled';

  let scanQueued = false;

  function injectHideStyle() {
    if (document.getElementById('cbh-style')) return;
    const style = document.createElement('style');
    style.id = 'cbh-style';
    style.textContent = `html.${ACTIVE_CLASS} [${HIDE_MARK_ATTR}] { display: none !important; }`;
    (document.head || document.documentElement).appendChild(style);
  }

  function markMatchingButtons() {
    scanQueued = false;
    document.querySelectorAll(`button:not([${HIDE_MARK_ATTR}])`).forEach((button) => {
      if (button.textContent.trim() === TARGET_BUTTON_TEXT) {
        button.setAttribute(HIDE_MARK_ATTR, '');
      }
    });
  }

  // Canva mutates the DOM constantly; coalesce scans to one per frame.
  function queueScan() {
    if (scanQueued) return;
    scanQueued = true;
    requestAnimationFrame(markMatchingButtons);
  }

  function setActive(enabled) {
    document.documentElement.classList.toggle(ACTIVE_CLASS, enabled);
  }

  function hiddenCount() {
    return document.querySelectorAll(`[${HIDE_MARK_ATTR}]`).length;
  }

  function extensionAlive() {
    return typeof chrome !== 'undefined' && !!chrome.runtime && !!chrome.runtime.id;
  }

  function init() {
    injectHideStyle();
    markMatchingButtons();
    new MutationObserver(queueScan).observe(document.body, {
      childList: true,
      subtree: true,
    });

    if (!extensionAlive()) {
      // Extension was reloaded under us; keep the default (on) behaviour.
      setActive(true);
      return;
    }

    chrome.storage.sync.get({ [STORAGE_KEY]: true }, (data) => {
      if (chrome.runtime.lastError) return;
      setActive(data[STORAGE_KEY]);
    });

    chrome.storage.onChanged.addListener((changes, area) => {
      if (area === 'sync' && STORAGE_KEY in changes) {
        setActive(changes[STORAGE_KEY].newValue !== false);
      }
    });

    chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
      if (!message) return;
      if (message.type === 'cbh-toggle') {
        setActive(message.enabled);
      } else if (message.type === 'cbh-status') {
        markMatchingButtons();
        sendResponse({ hidden: hiddenCount() });
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
