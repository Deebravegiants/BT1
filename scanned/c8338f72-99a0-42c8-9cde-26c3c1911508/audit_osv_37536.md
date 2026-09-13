# [M] Tinyproxy HTTP request parsing desynchronization via case-sensitive Transfer-Encoding handling

## Summary
Severity: Medium
Advisory: CVE-2026-31842
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-31842
Type: osv

## Details
Tinyproxy through 1.11.3 is vulnerable to HTTP request parsing desynchronization due to a case-sensitive comparison of the Transfer-Encoding header in src/reqs.c. The is_chunked_transfer function uses strcmp to compare the header value against "chunked", even though RFC 7230 specifies that transfer-coding names are case-insensitive.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31842.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31842
- https://github.com/tinyproxy/tinyproxy/issues/604
- https://github.com/tinyproxy/tinyproxy
- https://datatracker.ietf.org/doc/html/rfc7230
