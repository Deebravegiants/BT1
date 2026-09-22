# [M] Plack::Middleware::Statsd versions before 0.9.0 for Perl may leak user IP addresses

## Summary
Severity: Medium
Advisory: CVE-2026-45179
Aliases: GHSA-9gwm-665p-w2xx
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-10
Source: https://osv.dev/vulnerability/CVE-2026-45179
Type: osv

## Details
Plack::Middleware::Statsd versions before 0.9.0 for Perl may leak user IP addresses.

If the communication channel to the statsd daemon is not secured (for example, by sending UDP packets to a host on another network), then users' IP addresses may be leaked.

Since version 0.9.0, the IP address is no longer logged to statsd unless configured. When configured, an HMAC signature of the IP address is logged instead.

## References
- http://www.openwall.com/lists/oss-security/2026/05/10/4
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45179.json
- https://github.com/robrwo/Plack-Middleware-Statsd/security/advisories/GHSA-9gwm-665p-w2xx
- https://metacpan.org/release/RRWO/Plack-Middleware-Statsd-v0.9.0/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-45179
- https://github.com/robrwo/Plack-Middleware-Statsd
