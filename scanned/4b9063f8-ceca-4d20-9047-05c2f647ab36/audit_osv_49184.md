# [M] CVE-2018-5170

## Summary
Severity: Medium
Advisory: CVE-2018-5170
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-5170
Type: osv

## Details
It is possible to spoof the filename of an attachment and display an arbitrary attachment name. This could lead to a user opening a remote attachment which is a different file type than expected. This vulnerability affects Thunderbird ESR < 52.8 and Thunderbird < 52.8.

## References
- http://www.securitytracker.com/id/1040946
- https://access.redhat.com/errata/RHSA-2018:1725
- https://access.redhat.com/errata/RHSA-2018:1726
- https://lists.debian.org/debian-lts-announce/2018/05/msg00013.html
- https://security.gentoo.org/glsa/201811-13
- https://usn.ubuntu.com/3660-1/
- https://www.mozilla.org/security/advisories/mfsa2018-13/
- https://www.debian.org/security/2018/dsa-4209
- https://bugzilla.mozilla.org/show_bug.cgi?id=1411732
