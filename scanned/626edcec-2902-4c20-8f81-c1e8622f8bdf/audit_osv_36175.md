# [M] Titra APIs have Improper Access Control

## Summary
Severity: Medium
Advisory: CVE-2026-21694
Aliases: GHSA-mr2r-wjf8-cj3c
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21694
Type: osv

## Details
Titra is open source project time tracking software. Versions 0.99.49 and below have Improper Access Control, allowing users to view and edit other users' time entries in private projects they have not been granted access to. This issue is fixed in version 0.99.50.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21694.json
- https://github.com/kromitgmbh/titra/security/advisories/GHSA-mr2r-wjf8-cj3c
- https://nvd.nist.gov/vuln/detail/CVE-2026-21694
- https://github.com/kromitgmbh/titra/commit/29e6b88eca005107729e45a6f1731cf0fa5f8938
