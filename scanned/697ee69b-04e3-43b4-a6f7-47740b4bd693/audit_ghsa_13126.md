# [H] Electron's Content-Secrity-Policy disabling eval not applied consistently in renderers with sandbox disabled

## Summary
Severity: High
Advisory: GHSA-gxh7-wv9q-fwfr
CVE: CVE-2023-23623
CWE: CWE-670
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-gxh7-wv9q-fwfr
Type: github-advisory

## Affected
- npm: `electron` — affected >=22.0.0-beta.1 <22.0.1
- npm: `electron` — affected >=23.0.0-alpha.1 <23.0.0-alpha.2

## Details
### Impact
A Content-Security-Policy that disables eval, specifically setting a `script-src` directive and _not_ providing `unsafe-eval` in that directive, is not respected in renderers that have sandbox and contextIsolation disabled.  i.e. `sandbox: false` and `contextIsolation: false` in the `webPreferences` object.

This resulted in incorrectly allowing usage of methods like `eval()` and `new Function`, which can result in an expanded attack surface.

### Patches
This issue only ever affected the 22 and 23 major versions of Electron and has been fixed in the latest versions of those release lines. Specifically, these versions contain the fixes:

- 22.0.1
- 23.0.0-alpha.2

We recommend all apps upgrade to the latest stable version of Electron, especially if they use `sandbox: false` or `contextIsolation: false`.

### Workarounds
If upgrading isn't possible, this issue can be addressed without upgrading by enabling at least one of `sandbox: true` or `contextIsolation: true` on all renderers.

```js
const mainWindow = new BrowserWindow({
  webPreferences: {
    sandbox: true,
  }
});
```

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org).

### Credit
Thanks to user @andreasdj for reporting this issue.

## References
- https://github.com/electron/electron/security/advisories/GHSA-gxh7-wv9q-fwfr
- https://nvd.nist.gov/vuln/detail/CVE-2023-23623
- https://github.com/electron/electron/pull/36667
- https://github.com/electron/electron/pull/36668
- https://github.com/electron/electron/commit/9e7fbc7021d8d716c43782249a552e55289c35db
- https://github.com/electron/electron
- https://github.com/electron/electron/releases/tag/v22.0.1
