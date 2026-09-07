# [M] Snipe-IT has an Open Redirect After User Edit

## Summary
Severity: Medium
Advisory: GHSA-wg2f-x2c2-c4rp
CVE: CVE-2026-55461
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-wg2f-x2c2-c4rp
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.2

## Details
### Impact
The user edit flow stores `url()->previous()` into Laravel's intended URL session value and later redirects with `redirect()->intended(...)` when `redirect_option=back` is submitted. Because the previous URL is derived from the attacker-controlled `Referer` header, an authenticated user performing a normal user-edit action can be redirected to an external attacker-controlled site.

An attacker who can cause a logged-in user with permission to edit a user record to open the edit page with an attacker-controlled `Referer` value.

The application can be used as a trusted redirector after a legitimate user edit action. This can support phishing or trust-boundary attacks against Snipe-IT users and matches a historical open redirect class where session-stored navigation context influences redirect destinations.


### Patches
Patched in  f4cac96358

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-wg2f-x2c2-c4rp
- https://nvd.nist.gov/vuln/detail/CVE-2026-55461
- https://github.com/grokability/snipe-it/commit/f4cac9635868c020174361ad7a80b2545a4e7623
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.6.2
