# [M] CVE-2026-19203

## Summary
Severity: Medium
Advisory: CVE-2026-19203
Aliases: GHSA-xc35-c22g-239h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-19203
Type: osv

## Details
A client may issue specially crafted HTTP/1.1 chunked requests to a Jetty server that cause Jetty and an intermediary proxy to interpret different request boundaries, potentially resulting in HTTP request smuggling.




This is caused by Jetty accepting a lone LF character as a terminator in parts of chunked request parsing. Depending on the Jetty version and configured HTTP compliance mode, this may occur in chunk extensions, chunk data termination, or trailer termination.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19203.json
- https://github.com/jetty/jetty.project/security/advisories/GHSA-xc35-c22g-239h
- https://nvd.nist.gov/vuln/detail/CVE-2026-19203
