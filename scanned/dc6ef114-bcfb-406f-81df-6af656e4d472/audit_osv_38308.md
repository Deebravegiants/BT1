# [M] wrong proxy connection reuse with credentials

## Summary
Severity: Medium
Advisory: CVE-2026-3784
Aliases: CURL-CVE-2026-3784
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-3784
Type: osv

## Details
curl would wrongly reuse an existing HTTP proxy connection doing CONNECT to a
server, even if the new request uses different credentials for the HTTP proxy.
The proper behavior is to create or use a separate connection.

## References
- http://www.openwall.com/lists/oss-security/2026/03/11/3
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://curl.se/docs/CVE-2026-3784.html
- https://curl.se/docs/CVE-2026-3784.json
- https://hackerone.com/reports/3584903
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3784.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3784
