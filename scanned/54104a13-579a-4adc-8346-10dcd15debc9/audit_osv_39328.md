# [H] Catalyst::Plugin::Statsd versions through 0.10.0 for Perl may leak session ids

## Summary
Severity: High
Advisory: CVE-2026-45180
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-10
Source: https://osv.dev/vulnerability/CVE-2026-45180
Type: osv

## Details
Catalyst::Plugin::Statsd versions through 0.10.0 for Perl may leak session ids.

If the communication channel to the statsd daemon is not secured (for example, by sending UDP packets to a host on another network), then users' session ids may be leaked.  This may allow an attacker to use session ids as authentication tokens.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-45179
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45180.json
- https://github.com/robrwo/CatalystX-Statsd/security/advisories/GHSA-gjvr-hq83-fc38
- https://github.com/robrwo/Plack-Middleware-Statsd/security/advisories/GHSA-9gwm-665p-w2xx
- https://metacpan.org/release/RRWO/Catalyst-Plugin-Statsd-v0.10.0/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-45180
- https://github.com/robrwo/CatalystX-Statsd
