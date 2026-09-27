# [M] CVE-2011-1488

## Summary
Severity: Medium
Advisory: CVE-2011-1488
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-14
Source: https://osv.dev/vulnerability/CVE-2011-1488
Type: osv

## Details
A memory leak in rsyslog before 5.7.6 was found in the way deamon processed log messages are logged when $RepeatedMsgReduction was enabled. A local attacker could use this flaw to cause a denial of the rsyslogd daemon service by crashing the service via a sequence of repeated log messages sent within short periods of time.

## References
- http://lists.opensuse.org/opensuse-security-announce/2011-04/msg00005.html
- https://access.redhat.com/security/cve/cve-2011-1488
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-1488
- https://security-tracker.debian.org/tracker/CVE-2011-1488
- http://lists.opensuse.org/opensuse-security-announce/2011-04/msg00005.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-1488
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-1488
- https://github.com/rsyslog/rsyslog/commit/1ef709cc97d54f74d3fdeb83788cc4b01f4c6a2a
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2011-1488
