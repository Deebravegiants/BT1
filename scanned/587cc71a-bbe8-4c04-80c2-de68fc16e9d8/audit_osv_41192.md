# [M] Apache Traffic Server: Memory-safety and path-traversal errors in the Cripts framework

## Summary
Severity: Medium
Advisory: CVE-2026-58177
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:H/SC:L/SI:L/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-58177
Type: osv

## Details
The Apache Traffic Server Cripts framework has out-of-bounds writes, path traversal, and use-after-free errors.

This issue affects Apache Traffic Server: from 10.0.0 through 10.1.3.

Users are recommended to upgrade to version 10.1.4, which fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58177.json
- https://lists.apache.org/thread/5prl9glcm9g2swnq9hqxvnokylm1gr6d
- https://nvd.nist.gov/vuln/detail/CVE-2026-58177
