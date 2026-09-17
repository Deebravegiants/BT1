# [M] CVE-2026-41664

## Summary
Severity: Medium
Advisory: CVE-2026-41664
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41664
Type: osv

## Details
Integer overflow in memory copy size calculation in Samsung Open Source ONE could lead to invalid memory operations with large tensor shapes.
Affected version is prior to commit  1.30.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41664.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41664
- https://github.com/Samsung/ONE/pull/16481
