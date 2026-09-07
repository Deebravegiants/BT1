# [M] HAX CMS: Stored XSS via '<video-player>' component allows arbitrary JavaScript execution and token theft

## Summary
Severity: Medium
Advisory: GHSA-2m6p-hm3w-6jm3
CVE: CVE-2026-46496
CWE: CWE-116, CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-2m6p-hm3w-6jm3
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <26.0.0
- npm: `@haxtheweb/video-player` — affected >=0 <26.0.0

## Details
### Summary
A stored cross-site scripting (XSS) vulnerability exists in HAX CMS due to improper sanitization of the `<video-player>` component.

The component allows `javascript:` URIs in the `source` attribute, which are executed when the page is viewed. This enables attackers to execute arbitrary JavaScript in the context of the victim’s browser and access sensitive data such as JWT tokens and more.

### Details
The vulnerability is present in the `<video-player>` web component used within the HAX CMS editor.

The application fails to validate or sanitize user-supplied input in the following attributes:
- `source`
- `source-data`

These attributes accept arbitrary URI schemes, including `javascript:`, which leads to execution of attacker-controlled JavaScript in the browser.

Example vulnerable usage:
```html
<video-player 
  source="javascript:alert(document.domain)" 
  source-type="external">
</video-player>
```


Because this content is stored and rendered to other users, the vulnerability is classified as a stored XSS.

The root cause is the lack of URI scheme validation and improper sanitization of component attributes before rendering.
Because this content is stored and rendered to other users, the vulnerability is classified as a stored XSS.

The root cause is the lack of URI scheme validation and improper sanitization of component attributes before rendering.


### PoC

Steps to reproduce:
1. Log in to HAX CMS as user.
2. Create a website or any page and switch to the HTML source editor (`<>`).
3. Insert the following payload:

```html
<video-player source="javascript:alert('JWT: '+localStorage.getItem('jwt').substring(0,30))" source-type="external"></video-player>
```
<img width="2456" height="1405" alt="image" src="https://github.com/user-attachments/assets/ea037043-7ff7-4840-bed0-1091692c6289" />


Save the page.

Reload or revisit or send the page.

Result
<img width="2468" height="1394" alt="image" src="https://github.com/user-attachments/assets/543bbf69-900d-4e2d-bd6b-0658fb5aa899" />


A JavaScript alert executes.
The JWT token is exposed.
This confirms arbitrary JavaScript execution in the victim’s browser.


### Impact

This vulnerability allows stored XSS leading to:

- Theft of JWT authentication tokens 
- Session hijacking
- Full account takeover
- Execution of arbitrary JavaScript in victim browsers

If an administrator views a malicious page, this can lead to full CMS compromise.

Attack complexity: Low  
Privileges required: Low (any authenticated user)  
User interaction: Required

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-2m6p-hm3w-6jm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-46496
- https://github.com/haxtheweb/issues
