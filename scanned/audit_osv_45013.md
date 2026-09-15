# [H] Plack::Middleware::Security::Common versions before 0.13.1 for Perl did not block header injections in request paths

## Summary
Severity: High
Advisory: CVE-2026-9658
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-9658
Type: osv

## Details
Plack::Middleware::Security::Common versions before 0.13.1 for Perl did not block header injections in request paths.

The header injection rule was ineffective at blocking header injections in the request paths unless they were double-encoded, for example,

  GET /path\r\nHTTP/1.1\r\nHost: secret.example.com

Note that it is unclear whether request paths with CRLF followed by additional headers would be blocked by reverse proxies, or how they would be processed by Plack-based servers.

## References
- http://www.openwall.com/lists/oss-security/2026/05/28/9
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9658.json
- https://metacpan.org/release/RRWO/Plack-Middleware-Security-Simple-v0.13.1/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-9658
- https://github.com/robrwo/Plack-Middleware-Security-Simple
