# [H] CVE-2016-7545

## Summary
Severity: High
Advisory: CVE-2016-7545
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-01-19
Source: https://osv.dev/vulnerability/CVE-2016-7545
Type: osv

## Details
SELinux policycoreutils allows local users to execute arbitrary commands outside of the sandbox via a crafted TIOCSTI ioctl call.

## References
- http://www.securitytracker.com/id/1037283
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UPRNK3PWMAVNJZ53YW5GOEOGJSFNAQIF/
- http://rhn.redhat.com/errata/RHSA-2016-2702.html
- http://rhn.redhat.com/errata/RHSA-2017-0535.html
- http://rhn.redhat.com/errata/RHSA-2017-0536.html
- http://www.openwall.com/lists/oss-security/2016/09/25/1
- http://www.securityfocus.com/bid/93156
- https://marc.info/?l=selinux&m=147465160112766&w=2
- https://github.com/SELinuxProject/selinux/commit/acca96a135a4d2a028ba9b636886af99c0915379
