# [C] CVE-2018-5148

## Summary
Severity: Critical
Advisory: CVE-2018-5148
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-5148
Type: osv

## Details
A use-after-free vulnerability can occur in the compositor during certain graphics operations when a raw pointer is used instead of a reference counted one. This results in a potentially exploitable crash. This vulnerability affects Firefox ESR < 52.7.3 and Firefox < 59.0.2.

## References
- http://www.securityfocus.com/bid/103506
- http://www.securitytracker.com/id/1040574
- https://lists.debian.org/debian-lts-announce/2018/03/msg00023.html
- https://usn.ubuntu.com/3609-1/
- https://access.redhat.com/errata/RHSA-2018:1098
- https://access.redhat.com/errata/RHSA-2018:1099
- https://www.debian.org/security/2018/dsa-4153
- https://www.mozilla.org/security/advisories/mfsa2018-10/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1440717
