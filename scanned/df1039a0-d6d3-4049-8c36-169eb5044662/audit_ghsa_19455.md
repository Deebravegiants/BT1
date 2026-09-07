# [M] tarteaucitron.js allows prototype pollution via custom text injection

## Summary
Severity: Medium
Advisory: GHSA-4hwx-xcc5-2hfc
CVE: CVE-2025-31475
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-4hwx-xcc5-2hfc
Type: github-advisory

## Affected
- npm: `tarteaucitronjs` — affected >=0 <1.20.1

## Details
A vulnerability was identified in `tarteaucitron.js`, where the `addOrUpdate` function, used for applying custom texts, did not properly validate input. This allowed an attacker with direct access to the site's source code or a CMS plugin to manipulate JavaScript object prototypes, leading to potential security risks such as data corruption or unintended code execution.

## Impact
An attacker with high privileges could exploit this vulnerability to:
- Modify object prototypes, affecting core JavaScript behavior,
- Cause application crashes or unexpected behavior,
- Potentially introduce further security vulnerabilities depending on the application's architecture.

## Fix https://github.com/AmauriC/tarteaucitron.js/commit/74c354c413ee3f82dff97a15a0a43942887c2b5b
The issue was resolved by ensuring that user-controlled inputs cannot modify JavaScript object prototypes.

## References
- https://github.com/AmauriC/tarteaucitron.js/security/advisories/GHSA-4hwx-xcc5-2hfc
- https://nvd.nist.gov/vuln/detail/CVE-2025-31475
- https://github.com/AmauriC/tarteaucitron.js/commit/74c354c413ee3f82dff97a15a0a43942887c2b5b
- https://github.com/AmauriC/tarteaucitron.js
