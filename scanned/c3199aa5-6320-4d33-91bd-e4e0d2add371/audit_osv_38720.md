# [M] CVE-2026-41665

## Summary
Severity: Medium
Advisory: CVE-2026-41665
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41665
Type: osv

## Details
Integer overflow in scratch buffer initialization size calculation in Samsung Open Source ONE cause incorrect memory initialization for large intermediate tensors.
Affected version is prior to commit  1.30.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41665.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41665
- https://github.com/Samsung/ONE/pull/16481
