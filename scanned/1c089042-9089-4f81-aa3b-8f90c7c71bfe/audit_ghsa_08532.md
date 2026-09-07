# [M] Snipe-IT has an open redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mghp-5cq4-v6mg
CVE: CVE-2026-44833
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-mghp-5cq4-v6mg
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.4.1

## Details
Open redirect vulnerability in Snipe-IT allows attackers to redirect users to malicious sites via unvalidated HTTP Referer header stored in session variable.

### Impact

-   **Phishing**: Redirect users to fake login pages to steal credentials
-   **Session Hijacking**: Redirect to attacker site that captures session cookies via JavaScript
-   **Malware Distribution**: Redirect to sites hosting malware or drive-by downloads
-   **Reputation Damage**: Users lose trust when redirected to malicious sites from legitimate application
-   **Social Engineering**: Use trusted Snipe-IT domain to increase phishing success rate

When the user clicks "Save", the application: 
1. Processes the form 
2. Checks `redirect_option` (if set to 'back') 
3. Calls `Helper::getRedirectOption()` 
4. Retrieves `back_url` from session: `https://evil.com/phishing?target=snipeit` 
5. Executes `redirect()->to($backUrl)` 
6. User is redirected to attacker's site

This would still require session poisoning, so the actual practical threat here is minimal. 

### Patches
Patched in https://github.com/grokability/snipe-it/commit/e37649212861a337e68a624e589c3540b7a82373, released in 8.4.1.

### Workarounds
 None.

### Resources
-   CWE-601: URL Redirection to Untrusted Site ('Open Redirect')
-   OWASP: Unvalidated Redirects and Forwards
-   Laravel Security: Safe Redirects

[snipeit_open_redirect_submission.md](https://github.com/user-attachments/files/27414869/snipeit_open_redirect_submission.md)

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-mghp-5cq4-v6mg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44833
- https://github.com/grokability/snipe-it/commit/e37649212861a337e68a624e589c3540b7a82373
- https://github.com/grokability/snipe-it
