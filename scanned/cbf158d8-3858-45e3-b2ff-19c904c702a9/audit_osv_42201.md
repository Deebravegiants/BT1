# [M] Apache Traffic Server: HTTP/2 and HTTP/3 dechunking removes per-stream buffer cap, allowing memory exhaustion

## Summary
Severity: Medium
Advisory: CVE-2026-65324
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-65324
Type: osv

## Details
Apache Traffic Server drops the per-stream buffer cap when dechunking HTTP/2 or HTTP/3 responses, letting a slow client exhaust server memory.

This issue affects Apache Traffic Server: from 8.0.0 through 8.1.9, from 9.0.0 through 9.2.14, from 10.0.0 through 10.1.3.

Users are recommended to upgrade to version 9.2.15 or 10.1.4, which fix the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65324.json
- https://lists.apache.org/thread/5prl9glcm9g2swnq9hqxvnokylm1gr6d
- https://nvd.nist.gov/vuln/detail/CVE-2026-65324
