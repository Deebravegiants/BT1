# [H] sending old referer

## Summary
Severity: High
Advisory: CVE-2026-9546
Aliases: CURL-CVE-2026-9546
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-9546
Type: osv

## Details
A vulnerability in libcurl caused the HTTP `Referer:` header to persist even
when explicitly cleared. While the documentation states that passing NULL to
`CURLOPT_REFERER` suppresses the header, the option failed to clear the
internal state. As a result the previous referrer string was erroneously
reused and sent in subsequent requests, potentially leaking sensitive
information to unintended servers.

## References
- https://curl.se/docs/CVE-2026-9546.html
- https://curl.se/docs/CVE-2026-9546.json
- https://hackerone.com/reports/3754343
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9546.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-9546
