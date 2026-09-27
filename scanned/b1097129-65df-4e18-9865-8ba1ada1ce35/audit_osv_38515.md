# [M] CVE-2026-40450

## Summary
Severity: Medium
Advisory: CVE-2026-40450
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-40450
Type: osv

## Details
Integer overflow in output tensor copy size calculation in Samsung Open Source ONE could cause incorrect copy length and memory corruption for oversized tensors.
Affected version is prior to commit  1.30.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40450.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40450
- https://github.com/Samsung/ONE/pull/16481
