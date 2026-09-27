# [H] Starman versions before 0.4018 for Perl allows HTTP Request Smuggling via Improper Header Precedence

## Summary
Severity: High
Advisory: CVE-2026-40560
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/CVE-2026-40560
Type: osv

## Details
Starman versions before 0.4018 for Perl allows HTTP Request Smuggling via Improper Header Precedence.

Starman incorrectly prioritizes "Content-Length" over "Transfer-Encoding: chunked" when both headers are present in an HTTP request. Per RFC 7230 3.3.3, Transfer-Encoding must take precedence.

An attacker could exploit this to smuggle malicious HTTP requests via a front-end reverse proxy.

## References
- http://www.openwall.com/lists/oss-security/2026/04/29/1
- https://cpan.org/modules
- https://datatracker.ietf.org/doc/html/rfc7230#section-3.3.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40560.json
- https://metacpan.org/release/MIYAGAWA/Starman-0.4018/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-40560
- https://github.com/miyagawa/Starman/commit/ced205f0805027e9d9c0731f8c40b104220604ed.patch
- https://github.com/miyagawa/Starman
