# [M] CVE-2015-5231

## Summary
Severity: Medium
Advisory: CVE-2015-5231
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-06-07
Source: https://osv.dev/vulnerability/CVE-2015-5231
Type: osv

## Details
The service daemon in CRIU does not properly restrict access to non-dumpable processes, which allows local users to obtain sensitive information via (1) process dumps or (2) ptrace access.

## References
- https://lists.openvz.org/pipermail/criu/2015-August/021847.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1256728
- http://lists.opensuse.org/opensuse-updates/2015-09/msg00030.html
- http://www.openwall.com/lists/oss-security/2015/08/25/5
