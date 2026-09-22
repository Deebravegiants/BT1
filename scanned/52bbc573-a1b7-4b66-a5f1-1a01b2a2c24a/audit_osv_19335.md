# [H] CVE-2021-20240

## Summary
Severity: High
Advisory: CVE-2021-20240
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2021-20240
Type: osv

## Details
A flaw was found in gdk-pixbuf in versions before 2.42.0. An integer wraparound leading to an out of bounds write can occur when a crafted GIF image is loaded. An attacker may cause applications to crash or could potentially execute code on the victim system. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B5H3GNVWMZTYZR3JBYCK57PF7PFMQBNP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BGZVCTH5O7WBJLYXZ2UOKLYNIFPVR55D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EANWYODLOJDFLMBH6WEKJJMQ5PKLEWML/
- https://bugzilla.redhat.com/show_bug.cgi?id=1926787
