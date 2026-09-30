# [H] CVE-2016-5259

## Summary
Severity: High
Advisory: CVE-2016-5259
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-08-05
Source: https://osv.dev/vulnerability/CVE-2016-5259
Type: osv

## Details
Use-after-free vulnerability in the CanonicalizeXPCOMParticipant function in Mozilla Firefox before 48.0 and Firefox ESR 45.x before 45.3 allows remote attackers to execute arbitrary code via a script that closes its own Service Worker within a nested sync event loop.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00004.html
- http://www.securityfocus.com/bid/92258
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00029.html
- http://www.securitytracker.com/id/1036508
- http://rhn.redhat.com/errata/RHSA-2016-1551.html
- http://www.debian.org/security/2016/dsa-3640
- http://www.mozilla.org/security/announce/2016/mfsa2016-73.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- https://security.gentoo.org/glsa/201701-15
- http://www.ubuntu.com/usn/USN-3044-1
- https://bugzilla.mozilla.org/show_bug.cgi?id=1282992
