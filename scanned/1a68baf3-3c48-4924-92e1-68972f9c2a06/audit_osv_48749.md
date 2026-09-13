# [H] CVE-2018-12386

## Summary
Severity: High
Advisory: CVE-2018-12386
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-12386
Type: osv

## Details
A vulnerability in register allocation in JavaScript can lead to type confusion, allowing for an arbitrary read and write. This leads to remote code execution inside the sandboxed content process when triggered. This vulnerability affects Firefox ESR < 60.2.2 and Firefox < 62.0.3.

## References
- https://security.gentoo.org/glsa/201810-01
- https://usn.ubuntu.com/3778-1/
- https://www.debian.org/security/2018/dsa-4310
- https://www.mozilla.org/security/advisories/mfsa2018-24/
- http://www.securityfocus.com/bid/105460
- http://www.securitytracker.com/id/1041770
- https://access.redhat.com/errata/RHSA-2018:2881
- https://access.redhat.com/errata/RHSA-2018:2884
- https://bugzilla.mozilla.org/show_bug.cgi?id=1493900
