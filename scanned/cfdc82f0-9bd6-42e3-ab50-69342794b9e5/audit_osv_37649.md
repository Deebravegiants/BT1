# [C] HTTP::Session versions before 0.54 for Perl defaults to using insecurely generated session ids

## Summary
Severity: Critical
Advisory: CVE-2026-3256
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-28
Source: https://osv.dev/vulnerability/CVE-2026-3256
Type: osv

## Details
HTTP::Session versions before 0.54 for Perl defaults to using insecurely generated session ids.

HTTP::Session defaults to using HTTP::Session::ID::SHA1 to generate session ids using a SHA-1 hash seeded with the built-in rand function, the high resolution epoch time, and the PID. The PID will come from a small set of numbers, and the epoch time may be guessed, if it is not leaked from the HTTP Date header. The built-in rand function is unsuitable for cryptographic usage.

The distribution includes HTTP::session::ID::MD5 which contains a similar flaw, but uses the MD5 hash instead.

## References
- http://www.openwall.com/lists/oss-security/2026/03/28/5
- https://cpan.org/modules
- https://metacpan.org/release/KTAT/http-session-0.53/source/lib/HTTP/Session/ID/MD5.pm
- https://metacpan.org/release/KTAT/http-session-0.53/source/lib/HTTP/Session/ID/SHA1.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3256.json
- https://metacpan.org/release/TOKUHIROM/http-session-0.54/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-3256
- https://github.com/tokuhirom/http-session
- https://security.metacpan.org/docs/guides/random-data-for-security.html
