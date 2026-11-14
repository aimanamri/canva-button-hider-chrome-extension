'use strict';

const STORAGE_KEY = 'enabled';

function paintBadge(enabled) {
  chrome.action.setBadgeText({ text: enabled ? '' : 'OFF' });
  chrome.action.setBadgeBackgroundColor({ color: '#6b7280' });
  chrome.action.setTitle({
    title: `Canva Button Hider (${enabled ? 'on' : 'off'})`,
  });
}

function syncBadge() {
  chrome.storage.sync.get({ [STORAGE_KEY]: true }, (data) => {
    paintBadge(data[STORAGE_KEY]);
  });
}

chrome.runtime.onInstalled.addListener(syncBadge);
chrome.runtime.onStartup.addListener(syncBadge);

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'sync' && STORAGE_KEY in changes) {
    paintBadge(changes[STORAGE_KEY].newValue !== false);
  }
});

chrome.commands.onCommand.addListener((command) => {
  if (command !== 'toggle-hider') return;
  chrome.storage.sync.get({ [STORAGE_KEY]: true }, (data) => {
    chrome.storage.sync.set({ [STORAGE_KEY]: !data[STORAGE_KEY] });
  });
});
