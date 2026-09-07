# [M] Powermail TYPO3 extension Broken Access Control in the OutputController

## Summary
Severity: Medium
Advisory: GHSA-9jqr-5x45-pgw8
CVE: CVE-2024-45233
CWE: CWE-284, CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L/E:F/RL:O/RC:C (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-9jqr-5x45-pgw8
Type: github-advisory

## Affected
- Packagist: `in2code/powermail` — affected >=0 <7.5.0
- Packagist: `in2code/powermail` — affected >=8.0.0 <8.5.0
- Packagist: `in2code/powermail` — affected >=9.0.0 <10.9.0
- Packagist: `in2code/powermail` — affected >=11.0.0 <12.4.0

## Details
An issue was discovered in powermail extension through 12.3.5 for TYPO3. Several actions in the OutputController can directly be called, due to missing or insufficiently implemented access checks, resulting in Broken Access Control. Depending on the configuration of the Powermail Frontend plugins, an unauthenticated attacker can exploit this to edit, update, delete, or export data of persisted forms. This can only be exploited when the Powermail Frontend plugins are used. The fixed versions are 7.5.0, 8.5.0, 10.9.0, and 12.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45233
- https://github.com/in2code-de/powermail/commit/04a010c4009202e8e1b4c72accd4d7b2771b80b3
- https://github.com/in2code-de/powermail/commit/2c8a1bf7669eb0661e8a93164f57e4b653ac3408
- https://github.com/in2code-de/powermail/commit/6e94ec5e0c7b553c467b826df1b922db6c2ad08e
- https://github.com/in2code-de/powermail/commit/f56f8eefe151ad67cbd32c21f1106953b8e4f19f
- https://github.com/in2code-de/powermail
- https://typo3.org/security/advisory/typo3-ext-sa-2024-006
