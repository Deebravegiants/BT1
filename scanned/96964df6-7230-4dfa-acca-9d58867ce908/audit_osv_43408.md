# [C] Plack::Middleware::XSendfile versions through 1.0053 for Perl can allow client-controlled path rewriting

## Summary
Severity: Critical
Advisory: CVE-2026-7381
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-7381
Type: osv

## Details
Plack::Middleware::XSendfile versions through 1.0053 for Perl can allow client-controlled path rewriting.

Plack::Middleware::XSendfile allows the variation setting (sendfile type) to be set by the client via the X-Sendfile-Type header, if it is not considered in the middleware constructor or the Plack environment.

A malicious client can set the X-Sendfile-Type header to "X-Accel-Redirect" to services running behind nginx reverse proxies, and then set the X-Accel-Mapping to map the path to an arbitrary file on the server.

Since 1.0053, Plack::Middleware::XSendfile is deprecated and will be removed from future releases of Plack.

This is similar to CVE-2025-61780 for Rack::Sendfile, although Plack::Middleware::XSendfile has some mitigations that disallow regular expressions to be used in the mapping, and only apply the mapping for the "X-Accel-Redirect" type.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7381.json
- https://metacpan.org/release/MIYAGAWA/Plack-1.0053/changes
- https://nvd.nist.gov/vuln/detail/CVE-2025-61780
- https://nvd.nist.gov/vuln/detail/CVE-2026-7381
- https://github.com/plack/Plack
- https://metacpan.org/release/MIYAGAWA/Plack-1.0053/view/lib/Plack/Middleware/XSendfile.pm#DEPRECATION-NOTICE
