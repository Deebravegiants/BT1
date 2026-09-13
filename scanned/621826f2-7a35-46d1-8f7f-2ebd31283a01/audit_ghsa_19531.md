# [M] tarteaucitron.js allows UI manipulation via unrestricted CSS injection

## Summary
Severity: Medium
Advisory: GHSA-7524-3396-fqv3
CVE: CVE-2025-31138
CWE: CWE-1021
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-7524-3396-fqv3
Type: github-advisory

## Affected
- npm: `tarteaucitronjs` — affected >=0 <1.20.1

## Details
A vulnerability was identified in `tarteaucitron.js`, where user-controlled inputs for element dimensions (`width` and `height`) were not properly validated. This allowed an attacker with direct access to the site's source code or a CMS plugin to set values like `100%;height:100%;position:fixed;`, potentially covering the entire viewport and facilitating clickjacking attacks.

## Impact
An attacker with high privileges could exploit this vulnerability to:
- Overlay malicious UI elements on top of legitimate content,
- Trick users into interacting with hidden elements (clickjacking),
- Disrupt the intended functionality and accessibility of the website.

## Fix https://github.com/AmauriC/tarteaucitron.js/commit/25fcf828aaa55306ddc09cfbac9a6f8f126e2d07
The issue was resolved by enforcing strict validation and sanitization of user-provided CSS values to prevent unintended UI manipulation.

## References
- https://github.com/AmauriC/tarteaucitron.js/security/advisories/GHSA-7524-3396-fqv3
- https://nvd.nist.gov/vuln/detail/CVE-2025-31138
- https://github.com/AmauriC/tarteaucitron.js/commit/25fcf828aaa55306ddc09cfbac9a6f8f126e2d07
- https://github.com/AmauriC/tarteaucitron.js
