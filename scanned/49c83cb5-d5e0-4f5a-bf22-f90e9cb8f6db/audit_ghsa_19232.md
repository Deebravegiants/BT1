# [H] The Front End User Registration extension for TYPO3 (sr_feuser_register) allows Insecure Direct Object Reference

## Summary
Severity: High
Advisory: GHSA-cvgc-mx2w-h3w8
CVE: CVE-2025-48205
CWE: CWE-425, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-cvgc-mx2w-h3w8
Type: github-advisory

## Affected
- Packagist: `sjbr/sr-feuser-register` — affected >=5.1.0 <12.5.0

## Details
The sr_feuser_register extension through 12.4.8 for TYPO3 allows Insecure Direct Object Reference. This allows attackers to read arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48205
- https://codeberg.org/sjbr/sr-feuser-register
- https://codeberg.org/sjbr/sr-feuser-register/commit/be44f61a475371c36b2035cbb523b56f5e34267d
- https://typo3.org/security/advisory/typo3-ext-sa-2025-008
