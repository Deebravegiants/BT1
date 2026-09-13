# [M] Possible stack overflow due to a string encoding processing error

## Summary
Severity: Medium
Advisory: CVE-2024-32669
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-09
Source: https://osv.dev/vulnerability/CVE-2024-32669
Type: osv

## Details
Improper Input Validation vulnerability in Samsung Open Source escargot JavaScript engine allows Overflow Buffers.
However, it occurs in the test code and does not include in the release.

This issue affects escargot: 4.0.0.

## References
- https://github.com/Samsung/escargot/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32669.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32669
- https://github.com/Samsung/escargot/pull/1326
