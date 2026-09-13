# [H] CVE-2016-4444

## Summary
Severity: High
Advisory: CVE-2016-4444
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2016-4444
Type: osv

## Details
The allow_execmod plugin for setroubleshoot before 3.2.23 allows local users to execute arbitrary commands by triggering an execmod SELinux denial with a crafted binary filename, related to the commands.getstatusoutput function.

## References
- http://www.securityfocus.com/bid/91476
- http://www.securitytracker.com/id/1036144
- https://access.redhat.com/errata/RHSA-2016:1293
- https://rhn.redhat.com/errata/RHSA-2016-1267.html
- http://seclists.org/oss-sec/2016/q2/575
- https://bugzilla.redhat.com/show_bug.cgi?id=1332644
- https://github.com/fedora-selinux/setroubleshoot/commit/5cd60033ea7f5bdf8c19c27b23ea2d773d9b09f5
