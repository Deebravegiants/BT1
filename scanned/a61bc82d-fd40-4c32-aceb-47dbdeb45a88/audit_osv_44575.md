# [C] HTTP::Daemon versions before 6.17 for Perl allow OS command injection via send_file()

## Summary
Severity: Critical
Advisory: CVE-2026-8450
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-8450
Type: osv

## Details
HTTP::Daemon versions before 6.17 for Perl allow OS command injection via send_file().

send_file() opens its string argument with Perl's 2-arg open(). The 2-arg form interprets magic prefixes: '| cmd' and 'cmd |' open a pipe to a subprocess, '> path' and '>> path' open the path for write or append.

Untrusted input passed to send_file() can run OS commands at the daemon process UID. The read-pipe form ('cmd |') also leaks subprocess stdout into the HTTP response body. The write-mode forms can create or truncate files at attacker chosen paths.

## References
- http://www.openwall.com/lists/oss-security/2026/05/27/5
- https://cpan.org/modules
- https://lists.debian.org/debian-lts-announce/2026/06/msg00028.html
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-8450.json
- https://access.redhat.com/errata/RHSA-2026:36187
- https://access.redhat.com/errata/RHSA-2026:36188
- https://access.redhat.com/errata/RHSA-2026:36189
- https://access.redhat.com/security/cve/CVE-2026-8450
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8450.json
- https://metacpan.org/release/OALDERS/HTTP-Daemon-6.17/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-8450
- https://bugzilla.redhat.com/show_bug.cgi?id=2481773
- https://github.com/libwww-perl/HTTP-Daemon/pull/89
- https://github.com/libwww-perl/HTTP-Daemon/commit/945d35141d94490f749640bd4390acd6a2193995.patch
- https://github.com/libwww-perl/HTTP-Daemon
