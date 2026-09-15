# [M] CVE-2026-40448

## Summary
Severity: Medium
Advisory: CVE-2026-40448
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-40448
Type: osv

## Details
Potential Integer overflow in tensor allocation size calculation could lead to insufficient memory allocation for large tensors in Samsung Open Source ONE.
Affected version is prior to commit  1.30.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40448.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40448
- https://github.com/Samsung/ONE/pull/16481
