# [H] Open WebUI has Stored XSS in Banner Component via Improper Sanitization Order

## Summary
Severity: High
Advisory: GHSA-cqp4-qqvg-3787
CVE: CVE-2026-45665
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-cqp4-qqvg-3787
Type: github-advisory

## Affected
- npm: `open-webui` — affected >=0 <0.8.0

## Details
### Summary
A Stored Cross-Site Scripting (XSS) vulnerability exists in the Banner component due to an improper sanitization order (specifically, DOMPurify is executed before the marked library).

This vulnerability allows a compromised or malicious administrator to plant a malicious payload in the global banner. Crucially, this vector enables Privilege Escalation, as the malicious banner is rendered for all users, including the Super Admin (Primary Admin).

Consequently, the payload successfully bypasses the existing security mechanism. An attacker can leverage this to steal the Super Admin's session token

### Details
Root Cause: The code attempts to sanitize the input using DOMPurify.sanitize() before parsing it with marked.parse().

DOMPurify cleans the raw input. Since [Link](javascript:alert(javascript:alert(localStorage.token))) is valid text (not HTML), it passes through DOMPurify unchanged.
marked handles the text and converts it into a clickable HTML link: <a href="javascript:alert(javascript:alert(localStorage.token))">Link</a>.
This resulting unsafe HTML is rendered directly via {@html ...} without further checks.

`src/lib/components/common/Banner.svelte` (Line 103)
```svelte
{@html marked.parse(DOMPurify.sanitize((banner?.content ?? '').replace(/\n/g, '<br>')))}
```
### POC
1. **Attacker Action:** Log in as a compromised Admin account and navigate to **Settings > Interface > UI > Banners**.
2. **Injection:** Add a new banner and enter the following payload in the content field. This payload creates a link that alerts the user's session token when clicked.
    ```markdown
    [Click for Security Update](javascript:alert(localStorage.token))
    ```
3. **Execution:** Click **Save**. The malicious banner is now stored and active.
4. **Victim Action (Privilege Escalation):** The **Primary Admin** logs in and sees the banner on the main dashboard. Believing it to be a system notification, they click the link.
    **Victim Dashboard View:**
    
<img width="880" height="245" alt="image" src="https://github.com/user-attachments/assets/b70d7f65-ab34-4634-9e78-2a8a7eda1439" />

5. **Result:** The JavaScript executes immediately within the Primary Admin's session, exposing their full-access token.

### Impact
Extend permissions and damage to the entire system. You need administrator privileges to create banners, but this vulnerability is important because it can attack primary administrators and other administrators.

Destination: Other Administrators /Primary Administrators.
Attack Vector: Corrupting all administrator accounts (even those with limited scope if future granular privileges exist or simply credentials are compromised) could allow an attacker to set traps for the default administrator.
The result: Unlike self-XSS or simple administrator configuration changes, this allows you to capture active sessions for the most privileged users and bypass authentication controls such as MFA (because the session is already active).

### Recommended Patch
Modify `src/lib/components/common/Banner.svelte` (Line 103):

```
{@html DOMPurify.sanitize(marked.parse((banner?.content ?? '').replace(/\n/g, '<br>')))}
```

## Resolution

Fixed in **v0.8.0**. [`src/lib/components/common/Banner.svelte:103`](https://github.com/open-webui/open-webui/blob/main/src/lib/components/common/Banner.svelte#L103) now applies the sanitization in the correct order: `DOMPurify.sanitize(marked.parse(...))`. `marked.parse` runs first and converts `[text](javascript:...)` markdown into the corresponding HTML link element; `DOMPurify.sanitize` then strips the `javascript:` URL and any other dangerous attributes/elements before the result reaches `{@html ...}`.

Users on `>= 0.8.0` are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-cqp4-qqvg-3787
- https://nvd.nist.gov/vuln/detail/CVE-2026-45665
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.8.0
