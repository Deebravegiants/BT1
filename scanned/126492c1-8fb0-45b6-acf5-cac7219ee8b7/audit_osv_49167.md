# [H] CVE-2018-5129

## Summary
Severity: High
Advisory: CVE-2018-5129
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-5129
Type: osv

## Details
A lack of parameter validation on IPC messages results in a potential out-of-bounds write through malformed IPC messages. This can potentially allow for sandbox escape through memory corruption in the parent process. This vulnerability affects Thunderbird < 52.7, Firefox ESR < 52.7, and Firefox < 59.

## References
- http://www.securityfocus.com/bid/103388
- https://access.redhat.com/errata/RHSA-2018:0527
- https://access.redhat.com/errata/RHSA-2018:0647
- https://lists.debian.org/debian-lts-announce/2018/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2018/03/msg00029.html
- https://usn.ubuntu.com/3545-1/
- https://www.mozilla.org/security/advisories/mfsa2018-06/
- http://www.securitytracker.com/id/1040514
- https://security.gentoo.org/glsa/201810-01
- https://usn.ubuntu.com/3596-1/
- https://www.debian.org/security/2018/dsa-4139
- https://www.mozilla.org/security/advisories/mfsa2018-09/
- https://access.redhat.com/errata/RHSA-2018:0526
- https://www.debian.org/security/2018/dsa-4155
- https://www.mozilla.org/security/advisories/mfsa2018-07/
- https://access.redhat.com/errata/RHSA-2018:0648
- https://security.gentoo.org/glsa/201811-13
- https://bugzilla.mozilla.org/show_bug.cgi?id=1428947
