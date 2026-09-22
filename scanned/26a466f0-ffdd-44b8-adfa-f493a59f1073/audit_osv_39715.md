# [M] Net::Statsd::Lite versions before 0.9.0 for Perl allowed metric injections

## Summary
Severity: Medium
Advisory: CVE-2026-46719
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-16
Source: https://osv.dev/vulnerability/CVE-2026-46719
Type: osv

## Details
Net::Statsd::Lite versions before 0.9.0 for Perl allowed metric injections.

The metric names were not checked for newlines, colons or pipes. Metrics generated from untrusted sources could inject additional statsd metrics.

## References
- http://www.openwall.com/lists/oss-security/2026/05/16/9
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46719.json
- https://metacpan.org/release/RRWO/Net-Statsd-Lite-v0.9.0/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-46719
- https://github.com/robrwo/Net-Statsd-Lite/commit/e1a8ab866d75c2827982134e9cf7e51a7f771153.patch
- https://github.com/robrwo/Net-Statsd-Lite
