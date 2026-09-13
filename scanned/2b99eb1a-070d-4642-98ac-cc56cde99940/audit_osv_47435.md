# [C] CVE-2016-5254

## Summary
Severity: Critical
Advisory: CVE-2016-5254
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-05
Source: https://osv.dev/vulnerability/CVE-2016-5254
Type: osv

## Details
Use-after-free vulnerability in the nsXULPopupManager::KeyDown function in Mozilla Firefox before 48.0 and Firefox ESR 45.x before 45.3 allows attackers to execute arbitrary code or cause a denial of service (heap memory corruption and application crash) by leveraging keyboard access to use the Alt key during selection of top-level menu items.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00029.html
- http://www.securitytracker.com/id/1036508
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00004.html
- http://www.securityfocus.com/bid/92261
- http://www.mozilla.org/security/announce/2016/mfsa2016-70.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.ubuntu.com/usn/USN-3044-1
- https://security.gentoo.org/glsa/201701-15
- http://rhn.redhat.com/errata/RHSA-2016-1551.html
- http://www.debian.org/security/2016/dsa-3640
- https://bugzilla.mozilla.org/show_bug.cgi?id=1266963
