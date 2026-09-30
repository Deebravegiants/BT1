# [M] HTTP::Tiny versions before 0.093 for Perl do not validate CRLF in HTTP request lines or control field header values

## Summary
Severity: Medium
Advisory: CVE-2026-7010
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-7010
Type: osv

## Details
HTTP::Tiny versions before 0.093 for Perl do not validate CRLF in HTTP request lines or control field header values.

The unvalidated inputs are the method and URI in the request line, the URL host that becomes the `Host:` header, and HTTP/1.1 control data field values.

An attacker who controls one of these inputs, for example a user supplied URL passed to a webhook or URL fetch endpoint, can inject additional headers and smuggle requests to the upstream server.

## References
- http://www.openwall.com/lists/oss-security/2026/05/11/17
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7010.json
- https://metacpan.org/release/HAARG/HTTP-Tiny-0.093-TRIAL/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-7010
- https://github.com/Perl-Toolchain-Gang/HTTP-Tiny/commit/d73c7651e82ace02693842df55928b6c3ae7c38d.patch
- https://github.com/Perl-Toolchain-Gang/HTTP-Tiny
