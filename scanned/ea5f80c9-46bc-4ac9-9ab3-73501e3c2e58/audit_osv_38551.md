# [M] Starlet versions through 0.31 for Perl allows HTTP Request Smuggling via Improper Header Precedence

## Summary
Severity: Medium
Advisory: CVE-2026-40561
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-03
Source: https://osv.dev/vulnerability/CVE-2026-40561
Type: osv

## Details
Starlet versions through 0.31 for Perl allows HTTP Request Smuggling via Improper Header Precedence.

Starlet incorrectly prioritizes "Content-Length" over "Transfer-Encoding: chunked" when both headers are present in an HTTP request. Per RFC 7230 3.3.3, Transfer-Encoding must take precedence.

An attacker could exploit this to smuggle malicious HTTP requests via a front-end reverse proxy.

## References
- http://www.openwall.com/lists/oss-security/2026/05/03/1
- https://cpan.org/modules
- https://datatracker.ietf.org/doc/html/rfc7230#section-3.3.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40561.json
- https://metacpan.org/release/KAZUHO/Starlet-0.32/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-40561
- https://github.com/kazuho/Starlet/commit/a7d5dfd1862aafa43e5eaca0fdb6acf4cc15b2d0.patch
- https://github.com/kazuho/Starlet
