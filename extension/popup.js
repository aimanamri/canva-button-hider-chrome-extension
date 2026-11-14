(() => {
  'use strict';

  const STORAGE_KEY = 'enabled';
  const CANVA_DESIGN_PATTERN = /^https:\/\/www\.canva\.com\/design\//;

  const toggleInput = document.getElementById('toggleInput');
  const statusText = document.getElementById('statusText');
  const pill = document.getElementById('pageStatus');
  const pillText = document.getElementById('pageStatusText');

  document.getElementById('version').textContent = chrome.runtime.getManifest().version;

  let enabled = true;
  let activeTab = null;
  let hiddenOnPage = null; // null = unknown / not a Canva page

  function renderPill() {
    let state = 'idle';
    let text = 'Open a Canva design to use this';

    if (activeTab) {
      if (!enabled) {
        state = 'off';
        text = 'Paused: the button is showing on this tab';
      } else if (hiddenOnPage === null) {
        state = 'waiting';
        text = 'Reload this tab to activate';
      } else if (hiddenOnPage > 0) {
        state = 'hidden';
        text = 'Hidden on this tab';
      } else {
        state = 'idle';
        text = 'Active. No "Send to teacher" button here';
      }
    }
    pill.dataset.state = state;
    pillText.textContent = text;
  }

  function render(zap) {
    toggleInput.checked = enabled;
    document.body.dataset.enabled = String(enabled);
    statusText.textContent = enabled ? 'On. Button is hidden' : 'Off. Button is visible';
    if (zap && enabled) {
      document.body.classList.remove('zap');
      void document.body.offsetWidth; // restart animation
      document.body.classList.add('zap');
    }
    renderPill();
  }

  function askTabForStatus() {
    if (!activeTab) return;
    chrome.tabs.sendMessage(activeTab.id, { type: 'cbh-status' }, (res) => {
      hiddenOnPage = chrome.runtime.lastError || !res ? null : res.hidden;
      renderPill();
    });
  }

  function notifyCanvaTabs() {
    chrome.tabs.query({ url: 'https://www.canva.com/design/*' }, (tabs) => {
      tabs.forEach((tab) => {
        chrome.tabs.sendMessage(tab.id, { type: 'cbh-toggle', enabled }, () => {
          void chrome.runtime.lastError; // stale tab; storage change covers it
        });
      });
    });
  }

  toggleInput.addEventListener('change', () => {
    enabled = toggleInput.checked;
    render(true);
    chrome.storage.sync.set({ [STORAGE_KEY]: enabled });
    notifyCanvaTabs();
  });

  // Keep the popup in sync if the keyboard shortcut flips the setting.
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === 'sync' && STORAGE_KEY in changes) {
      enabled = changes[STORAGE_KEY].newValue !== false;
      render(false);
    }
  });

  chrome.storage.sync.get({ [STORAGE_KEY]: true }, (data) => {
    enabled = data[STORAGE_KEY];
    toggleInput.disabled = false;
    render(false);
  });

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tab = tabs[0];
    if (tab && tab.url && CANVA_DESIGN_PATTERN.test(tab.url)) {
      activeTab = tab;
      askTabForStatus();
    }
    renderPill();
  });
})();
