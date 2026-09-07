# [M] mailqueue TYPO3 extension affected by Insecure Deserialization in QueueableFileTransport

## Summary
Severity: Medium
Advisory: GHSA-ggff-9mj3-7246
CVE: CVE-2026-0895
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:L/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-ggff-9mj3-7246
Type: github-advisory

## Affected
- Packagist: `cpsit/typo3-mailqueue` — affected >=0 <0.4.3
- Packagist: `cpsit/typo3-mailqueue` — affected >=0.5.0 <0.5.1

## Details
## Description

The extension extends TYPO3’s FileSpool component, which was vulnerable to Insecure Deserialization prior to [TYPO3-CORE-SA-2026-004](https://typo3.org/security/advisory/typo3-core-sa-2026-004). Since the related fix is overwritten by the extension, using the extension with a patched TYPO3 core version still allows for Insecure Deserialization, because the affected vulnerable code was extracted from TYPO3 core to the extension.

More information about this vulnerability can be found in the related TYPO3 Core Security Advisory [TYPO3-CORE-SA-2026-004](https://typo3.org/security/advisory/typo3-core-sa-2026-004).

## References

* [TYPO3-EXT-SA-2026-001](https://typo3.org/security/advisory/typo3-ext-sa-2026-001)
* https://github.com/CPS-IT/mailqueue/commit/fd09aa4e1a751551bae4b228bee814e22f2048db
* https://github.com/CPS-IT/mailqueue/commit/12a0a35027bb5609917790a94e43bbf117abf733

## References
- https://github.com/CPS-IT/mailqueue/security/advisories/GHSA-ggff-9mj3-7246
- https://nvd.nist.gov/vuln/detail/CVE-2026-0895
- https://github.com/CPS-IT/mailqueue/commit/12a0a35027bb5609917790a94e43bbf117abf733
- https://github.com/CPS-IT/mailqueue/commit/fd09aa4e1a751551bae4b228bee814e22f2048db
- https://github.com/CPS-IT/mailqueue
- https://typo3.org/security/advisory/typo3-ext-sa-2026-001
