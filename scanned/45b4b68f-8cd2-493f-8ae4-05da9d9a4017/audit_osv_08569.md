# [H] CVE-2016-4446

## Summary
Severity: High
Advisory: CVE-2016-4446
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2016-4446
Type: osv

## Details
The allow_execstack plugin for setroubleshoot allows local users to execute arbitrary commands by triggering an execstack SELinux denial with a crafted filename, related to the commands.getoutput function.

## References
- http://www.securityfocus.com/bid/91427
- http://www.securitytracker.com/id/1036144
- https://access.redhat.com/errata/RHSA-2016:1293
- https://rhn.redhat.com/errata/RHSA-2016-1267.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1339250
- http://seclists.org/oss-sec/2016/q2/575
- https://github.com/fedora-selinux/setroubleshoot/commit/eaccf4c0d20a27d3df5ff6de8c9dcc80f6f40718
