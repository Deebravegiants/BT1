# [H] Electron Vulnerable to Code Execution by Re-Enabling Node.js Integration

## Summary
Severity: High
Advisory: GHSA-8xwg-wv7v-4vqp
CVE: CVE-2018-1000136
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-03-26
Source: https://github.com/advisories/GHSA-8xwg-wv7v-4vqp
Type: github-advisory

## Affected
- npm: `electron` — affected >=1.7.0 <1.7.13
- npm: `electron` — affected >=1.8.0 <1.8.4
- npm: `electron` — affected >=2.0.0-beta.1 <2.0.0-beta.5

## Details
A vulnerability has been discovered which allows Node.js integration to be re-enabled in some Electron applications that disable it.

For the application to be impacted by this vulnerability it must meet all of these conditions

- Runs on Electron 1.7, 1.8, or a 2.0.0-beta
- Allows execution of arbitrary remote code
- Disables Node.js integration
- Does not explicitly declare webviewTag: false in its webPreferences
- Does not enable the nativeWindowOption option
- Does not intercept new-window events and manually override event.newGuest without using the supplied options tag


## Recommendation

Update to `electron` version 1.7.13, 1.8.4, or 2.0.0-beta.5 or later.

If you are unable to update your Electron version can mitigate the vulnerability with the following code.

```js
app.on('web-contents-created', (event, win) => {
  win.on('new-window', (event, newURL, frameName, disposition,
                        options, additionalFeatures) => {
    if (!options.webPreferences) options.webPreferences = {};
    options.webPreferences.nodeIntegration = false;
    options.webPreferences.nodeIntegrationInWorker = false;
    options.webPreferences.webviewTag = false;
    delete options.webPreferences.preload;
  })
})

// and *IF* you don't use WebViews at all,
// you might also want
app.on('web-contents-created', (event, win) => {
  win.on('will-attach-webview', (event, webPreferences, params) => {
    event.preventDefault();
  })
})
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000136
- https://github.com/electron/electron/pull/12271
- https://github.com/electron/electron/pull/12292
- https://github.com/electron/electron/pull/12294
- https://github.com/electron/electron/commit/1a48ee28276e6588dbf4e70e58d78e7bfdc57043
- https://electronjs.org/blog/webview-fix
- https://github.com/electron/electron
- https://www.electronjs.org/blog/webview-fix
- https://www.npmjs.com/advisories/574
- https://www.trustwave.com/Resources/SpiderLabs-Blog/CVE-2018-1000136---Electron-nodeIntegration-Bypass
