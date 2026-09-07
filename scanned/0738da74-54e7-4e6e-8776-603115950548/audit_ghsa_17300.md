# [M] FeehiCMS fails to enforce server-side immutability

## Summary
Severity: Medium
Advisory: GHSA-qgc9-p7cj-jvh6
CVE: CVE-2025-63523
CWE: CWE-125
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-01
Source: https://github.com/advisories/GHSA-qgc9-p7cj-jvh6
Type: github-advisory

## Affected
- Packagist: `feehi/feehicms` — affected 2.1.1

## Details
FeehiCMS version 2.1.1 fails to enforce server-side immutability for parameters that are presented to clients as "read-only." An authenticated attacker can intercept and modify the parameter in transit and the backend accepts the changes. This can lead to unintended username changes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-63523
- https://github.com/liufee/cms/issues/77
- https://github.com/kiwi865/CVEs/blob/main/CVE-2025-63523.md
- https://github.com/liufee/cms
