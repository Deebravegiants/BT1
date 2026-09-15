# [M] Catalyst::Plugin::Static::Simple versions through 0.38 for Perl mark responses as publicly cacheable

## Summary
Severity: Medium
Advisory: CVE-2026-15743
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-15743
Type: osv

## Details
Catalyst::Plugin::Static::Simple versions through 0.38 for Perl mark responses as publicly cacheable.

The _serve_static method always sets the Cache-Control header to "public", with no means of overriding it.  This advises proxies that the content may be stored in a shared cache, and may be reused in responses to requests from other users. (This includes requests with an Authorization header.)

Configuring the expires time to "0" to disable caching, as documented, is ignored.

## References
- http://www.openwall.com/lists/oss-security/2026/08/20/18
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15743.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15743
- https://github.com/perl-catalyst/Catalyst-Plugin-Static-Simple/pull/3
- https://security.metacpan.org/patches/C/Catalyst-Plugin-Static-Simple/0.38/CVE-2026-15743-r1.patch
- https://github.com/perl-catalyst/Catalyst-Plugin-Static-Simple
- https://datatracker.ietf.org/doc/html/rfc9111
