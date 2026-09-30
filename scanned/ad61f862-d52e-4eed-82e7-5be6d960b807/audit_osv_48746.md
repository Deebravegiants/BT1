# [M] CVE-2018-12383

## Summary
Severity: Medium
Advisory: CVE-2018-12383
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-12383
Type: osv

## Details
If a user saved passwords before Firefox 58 and then later set a master password, an unencrypted copy of these passwords is still accessible. This is because the older stored password file was not deleted when the data was copied to a new format starting in Firefox 58. The new master password is added only on the new file. This could allow the exposure of stored password data outside of user expectations. This vulnerability affects Firefox < 62, Firefox ESR < 60.2.1, and Thunderbird < 60.2.1.

## References
- http://www.securityfocus.com/bid/105276
- https://lists.debian.org/debian-lts-announce/2018/11/msg00011.html
- http://www.securitytracker.com/id/1041610
- http://www.securitytracker.com/id/1041701
- https://access.redhat.com/errata/RHSA-2018:3458
- https://security.gentoo.org/glsa/201810-01
- https://security.gentoo.org/glsa/201811-13
- https://usn.ubuntu.com/3761-1/
- https://www.debian.org/security/2018/dsa-4304
- https://www.mozilla.org/security/advisories/mfsa2018-25/
- https://access.redhat.com/errata/RHSA-2018:3403
- https://usn.ubuntu.com/3793-1/
- https://www.debian.org/security/2018/dsa-4327
- https://www.mozilla.org/security/advisories/mfsa2018-23/
- https://access.redhat.com/errata/RHSA-2018:2834
- https://access.redhat.com/errata/RHSA-2018:2835
- https://www.mozilla.org/security/advisories/mfsa2018-20/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1475775
