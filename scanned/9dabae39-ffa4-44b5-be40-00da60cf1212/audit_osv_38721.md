# [M] CVE-2026-41666

## Summary
Severity: Medium
Advisory: CVE-2026-41666
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41666
Type: osv

## Details
Integer overflow in tensor copy size calculation in Samsung Open Source ONE could lead to out of bounds access during loop state propagation.
Affected version is prior to commit  1.30.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41666.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41666
- https://github.com/Samsung/ONE/pull/16481
