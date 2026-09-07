# [M] Bagisto has HTML Filter Bypass that Enables Stored XSS

## Summary
Severity: Medium
Advisory: GHSA-2mwc-h2mg-v6p8
CVE: CVE-2026-21451
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N/E:P (CVSS_V4)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-2mwc-h2mg-v6p8
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <2.3.10

## Details
### Summary
A stored Cross-Site Scripting (XSS) vulnerability exists in Bagisto 2.3.8 within the CMS page editor. Although the platform normally attempts to sanitize `<script>` tags, the filtering can be bypassed by manipulating the raw HTTP POST request before submission. As a result, arbitrary JavaScript can be stored in the CMS content and executed whenever the page is viewed or edited.
This exposes administrators to a high-severity risk, including complete account takeover, backend hijacking, and malicious script execution.

### Details
Bagisto’s CMS editor includes an HTML sanitation mechanism intended to protect against script injection by wrapping raw script content in `<div>` elements. However, this mechanism is applied only to requests submitted through the UI. When the CMS update request is intercepted and modified at the HTTP level, the sanitation layer fails to strip or encode embedded `<script>` tags.

Because the back-end trusts the manipulated request, the malicious script is stored in the database exactly as submitted. When an administrator opens the CMS page (either in the editor or in the storefront), the JavaScript executes in the browser context with full admin privileges.

The vulnerability stems from insufficient server-side sanitization.
Sanitization logic appears to rely on client-side or UI-layer controls, leaving the underlying HTTP endpoint unprotected.

### PoC
* A Bagisto 2.3.8 installation with access to the admin panel
* Ability to intercept and modify outgoing CMS update requests (e.g., via a proxy tool)
* Editing any CMS page (such as /admin/cms/edit/{id})

By introducing unfiltered script content directly into the HTTP payload; bypassing the UI-level sanitization the CMS endpoint accepts and stores the malicious JS.

### Steps to Reproduce

1. Log in as admin
2. Navigate to: /admin/cms/edit/1
3. Intercept the request (e.g., using Burp Suite)
4. Modify the en[html_content] field to include raw JavaScript:

<img width="1166" height="580" alt="unnamed" src="https://github.com/user-attachments/assets/2163def6-02a4-46d3-b0bf-a66dcce00f55" />

<img width="1167" height="573" alt="unnamed" src="https://github.com/user-attachments/assets/ffe540aa-f7f9-4dc9-b934-6d2798cafa0a" />



> A video PoC has been prepared showing:

* Normal CMS editing behavior
* How the sanitation process is expected to work
* How altering the raw request bypasses sanitization
* Execution of the stored script once the page is loaded
This helps illustrate both expected behavior and actual vulnerability behavior clearly.

Video PoC: https://drive.google.com/file/d/1quGkBq1zwRhVrlJtVeDk9iQeUzqIyOM-/view

### Impact
* Administrator account takeover
* Session hijacking
* Unauthorized actions performed in admin context
* Defacement or injection of malicious content into public pages
* Potential expansion into full application compromise

### Recommendations

Implement server-side sanitization (e.g., HTMLPurifier or Laravel Purifier) to strip or encode <script> tags regardless of how the request is manipulated.

## References
- https://github.com/bagisto/bagisto/security/advisories/GHSA-2mwc-h2mg-v6p8
- https://nvd.nist.gov/vuln/detail/CVE-2026-21451
- https://github.com/bagisto/bagisto/commit/f533b1cd9c80896792da60976179c95573d78b79
- https://github.com/bagisto/bagisto
- https://github.com/bagisto/bagisto/releases/tag/v2.3.10
