# [C] CVE-2019-11713

## Summary
Severity: Critical
Advisory: CVE-2019-11713
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-11713
Type: osv

## Details
A use-after-free vulnerability can occur in HTTP/2 when a cached HTTP/2 stream is closed while still in use, resulting in a potentially exploitable crash. This vulnerability affects Firefox ESR < 60.8, Firefox < 68, and Thunderbird < 60.8.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00073.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00010.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00058.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00009.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00001.html
- https://www.mozilla.org/security/advisories/mfsa2019-21/
- https://www.mozilla.org/security/advisories/mfsa2019-23/
- https://security.gentoo.org/glsa/201908-12
- https://security.gentoo.org/glsa/201908-20
- https://www.mozilla.org/security/advisories/mfsa2019-22/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1528481
