# [H] CVE-2018-11233

## Summary
Severity: High
Advisory: CVE-2018-11233
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-05-30
Source: https://osv.dev/vulnerability/CVE-2018-11233
Type: osv

## Details
In Git before 2.13.7, 2.14.x before 2.14.4, 2.15.x before 2.15.2, 2.16.x before 2.16.4, and 2.17.x before 2.17.1, code to sanity-check pathnames on NTFS can result in reading out-of-bounds memory.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00003.html
- http://www.securityfocus.com/bid/104346
- http://www.securitytracker.com/id/1040991
- https://access.redhat.com/errata/RHSA-2018:2147
- https://marc.info/?l=git&m=152761328506724&w=2
- https://security.gentoo.org/glsa/201805-13
- https://usn.ubuntu.com/3671-1/
