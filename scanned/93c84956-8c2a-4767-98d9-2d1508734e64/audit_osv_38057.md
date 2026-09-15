# [M] cpp-httplib: HTTP Request Smuggling via Unconsumed GET Request Body

## Summary
Severity: Medium
Advisory: CVE-2026-34441
Aliases: GHSA-jv63-rm9j-6jwc
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34441
Type: osv

## Details
cpp-httplib is a C++11 single-file header-only cross platform HTTP/HTTPS library. Prior to version 0.40.0, cpp-httplib is vulnerable to HTTP Request Smuggling. The server's static file handler serves GET responses without consuming the request body. On HTTP/1.1 keep-alive connections, the unread body bytes remain on the TCP stream and are interpreted as the start of a new HTTP request. An attacker can embed an arbitrary HTTP request inside the body of a GET request, which the server processes as a separate request. This issue has been patched in version 0.40.0.

## References
- https://github.com/yhirose/cpp-httplib/releases/tag/v0.40.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34441.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-jv63-rm9j-6jwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-34441
