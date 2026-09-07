# [H] Stored XSS via <iframe> in HAX CMS allows access to sensitive client-side data and account takeover

## Summary
Severity: High
Advisory: GHSA-jh3h-rpxg-fr36
CVE: CVE-2026-46396
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-jh3h-rpxg-fr36
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <26.0.0
- npm: `@haxtheweb/video-player` — affected >=0 <26.0.0
- npm: `@haxtheweb/iframe-loader` — affected >=0 <26.0.0

## Details
### Summary
A stored cross-site scripting (XSS) vulnerability exists in HAX CMS due to improper sanitization of `<iframe>` elements.

The application allows `javascript:` URIs in the `src` attribute, which are executed when a malicious page is viewed. This enables attackers to execute arbitrary JavaScript in the context of the victim’s browser and access sensitive data exposed to client-side scripts.

### Details
Successful exploitation allows access to any data available in the browser context, including:

- Authentication tokens (e.g., JWT)
- Session cookies (if not protected with HttpOnly)
- Application configuration (e.g., window.appSettings)
- User-specific data accessible via APIs

This significantly increases the impact beyond simple script execution.

### PoC
Steps to reproduce:

1. Log in to HAX CMS as any authenticated user.
2. Create a new page or edit an existing page.
3. Open the HTML source editor (`<>`).
4. Insert the following payload:

```html
<iframe srcdoc="&lt;script&gt;
    (function(){
        try {
            var jwt = parent.window.appSettings.jwt;
            alert('Stolen JWT:\n' + jwt);
        } catch(e) {
            alert('Error: ' + e.message);
        }
    })();
&lt;/script&gt;" style="display:none" sandbox="allow-scripts allow-same-origin"></iframe>
```
<img width="2446" height="1319" alt="image" src="https://github.com/user-attachments/assets/daea3b41-8c72-4f6c-ab32-34c688bbd251" />


<img width="2464" height="1397" alt="image" src="https://github.com/user-attachments/assets/911cbd42-db50-454a-b178-51555e0db79c" />



<img width="2466" height="1409" alt="webhook`" src="https://github.com/user-attachments/assets/8a286435-98f4-418c-a596-d0c19556696a" />

### Impact
This vulnerability allows stored XSS leading to:

- Execution of arbitrary JavaScript in victim browsers
- Access to sensitive client-side data, including authentication tokens and session identifiers
- Unauthorized API actions performed on behalf of the victim
- Session hijacking and full account takeover

Because the application exposes authentication data in the client-side environment, exploitation of this vulnerability can lead to complete compromise of user accounts and site content.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-jh3h-rpxg-fr36
- https://nvd.nist.gov/vuln/detail/CVE-2026-46396
- https://github.com/haxtheweb/issues
