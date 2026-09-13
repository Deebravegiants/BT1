# [M] Exfiltration of hashed SMB credentials on Windows via file:// redirect

## Summary
Severity: Medium
Advisory: GHSA-p2jh-44qj-pf2v
CVE: CVE-2022-36077
CWE: CWE-200, CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-p2jh-44qj-pf2v
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <18.3.7
- npm: `electron` — affected >=20.0.0-beta.1 <20.0.1
- npm: `electron` — affected >=19.0.0-beta.1 <19.0.11

## Details
### Impact
When following a redirect, Electron delays a check for redirecting to file:// URLs from other schemes. The contents of the file is not available to the renderer following the redirect, but if the redirect target is a SMB URL such as `file://some.website.com/`, then in some cases, Windows will connect to that server and attempt NTLM authentication, which can include sending hashed credentials.

### Patches
This issue has been fixed in all current stable versions of Electron. Specifically, these versions contain the fixes:

- 21.0.0-beta.1
- 20.0.1
- 19.0.11
- 18.3.7

We recommend all apps upgrade to the latest stable version of Electron.

### Workarounds
If upgrading isn't possible, this issue can be addressed without upgrading by preventing redirects to file:// URLs in the `WebContents.on('will-redirect')` event, for all WebContents:

```js
app.on('web-contents-created', (e, webContents) => {
  webContents.on('will-redirect', (e, url) => {
    if (/^file:/.test(url)) e.preventDefault()
  })
})
```

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org).

### Credit
Thanks to user @coolcoolnoworries for reporting this issue.

## References
- https://github.com/electron/electron/security/advisories/GHSA-p2jh-44qj-pf2v
- https://nvd.nist.gov/vuln/detail/CVE-2022-36077
- https://github.com/electron/electron
