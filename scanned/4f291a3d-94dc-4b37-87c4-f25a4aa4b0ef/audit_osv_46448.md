# [M] CVE-2011-1489

## Summary
Severity: Medium
Advisory: CVE-2011-1489
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-14
Source: https://osv.dev/vulnerability/CVE-2011-1489
Type: osv

## Details
A memory leak in rsyslog before 5.7.6 was found in the way deamon processed log messages were logged when multiple rulesets were used and some output batches contained messages belonging to more than one ruleset. A local attacker could cause denial of the rsyslogd daemon service via a log message belonging to more than one ruleset.

## References
- http://lists.opensuse.org/opensuse-security-announce/2011-04/msg00005.html
- https://access.redhat.com/security/cve/cve-2011-1489
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-1489
- https://github.com/rsyslog/rsyslog/commit/1ef709cc97d54f74d3fdeb83788cc4b01f4c6a2a
- https://security-tracker.debian.org/tracker/CVE-2011-1489
- http://lists.opensuse.org/opensuse-security-announce/2011-04/msg00005.html
- https://access.redhat.com/security/cve/cve-2011-1489
- https://access.redhat.com/security/cve/cve-2011-1489
- https://github.com/rsyslog/rsyslog/commit/1ef709cc97d54f74d3fdeb83788cc4b01f4c6a2a
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-1489
