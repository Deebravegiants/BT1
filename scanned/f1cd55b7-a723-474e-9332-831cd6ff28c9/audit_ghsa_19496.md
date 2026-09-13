# [M] tarteaucitron.js allows url scheme injection via unfiltered inputs

## Summary
Severity: Medium
Advisory: GHSA-p5g4-v748-6fh8
CVE: CVE-2025-31476
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-p5g4-v748-6fh8
Type: github-advisory

## Affected
- npm: `tarteaucitronjs` — affected >=0 <1.20.1

## Details
A vulnerability was identified in `tarteaucitron.js`, allowing a user with high privileges (access to the site's source code or a CMS plugin) to enter a URL containing an insecure scheme such as `javascript:alert()`. Before the fix, URL validation was insufficient, which could allow arbitrary JavaScript execution if a user clicked on a malicious link.

## Impact
An attacker with high privileges could insert a link exploiting an insecure URL scheme, leading to:
- Execution of arbitrary JavaScript code
- Theft of sensitive data through phishing attacks
- Modification of the user interface behavior

## Fix https://github.com/AmauriC/tarteaucitron.js/commit/2fa1e01023bce2e4b813200600bb1619d56ceb02
The issue was resolved by enforcing strict URL validation, ensuring that they start with `http://` or `https://` before being used.

## References
- https://github.com/AmauriC/tarteaucitron.js/security/advisories/GHSA-p5g4-v748-6fh8
- https://nvd.nist.gov/vuln/detail/CVE-2025-31476
- https://github.com/AmauriC/tarteaucitron.js/commit/2fa1e01023bce2e4b813200600bb1619d56ceb02
- https://github.com/AmauriC/tarteaucitron.js
