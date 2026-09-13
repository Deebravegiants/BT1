# [H] CVE-2016-4445

## Summary
Severity: High
Advisory: CVE-2016-4445
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2016-4445
Type: osv

## Details
The fix_lookup_id function in sealert in setroubleshoot before 3.2.23 allows local users to execute arbitrary commands as root by triggering an SELinux denial with a crafted file name, related to executing external commands with the commands.getstatusoutput function.

## References
- http://www.securityfocus.com/bid/91430
- http://www.securitytracker.com/id/1036144
- https://rhn.redhat.com/errata/RHSA-2016-1267.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1339183
- http://seclists.org/oss-sec/2016/q2/575
- https://github.com/fedora-selinux/setroubleshoot/commit/2d12677629ca319310f6263688bb1b7f676c01b7
