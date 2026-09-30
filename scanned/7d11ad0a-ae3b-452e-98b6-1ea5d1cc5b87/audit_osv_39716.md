# [M] Mojolicious::Plugin::Statsd versions through 0.04 for Perl allowed metric injections

## Summary
Severity: Medium
Advisory: CVE-2026-46740
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-46740
Type: osv

## Details
Mojolicious::Plugin::Statsd versions through 0.04 for Perl allowed metric injections.

The metric names and set values were not checked for newlines, colons or pipes. Metrics generated from untrusted sources could inject additional statsd metrics.

Version 0.06 changes the module from being a statsd client to using a separate statsd client. It defaults to using a version of Net::Statsd::Tiny that fixes a similar issue (CVE-2026-46720).

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-46720
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46740.json
- https://metacpan.org/release/RRWO/Mojolicious-Plugin-Statsd-0.06/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-46740
- https://github.com/robrwo/perl-Mojolicious-Plugin-Statsd/commit/f049156982a2c0b8050f173e24a04a29ddd64853.patch
- https://github.com/robrwo/perl-Mojolicious-Plugin-Statsd
