# [M] CVE-2019-11717

## Summary
Severity: Medium
Advisory: CVE-2019-11717
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-11717
Type: osv

## Details
A vulnerability exists where the caret ("^") character is improperly escaped constructing some URIs due to it being used as a separator, allowing for possible spoofing of origin attributes. This vulnerability affects Firefox ESR < 60.8, Firefox < 68, and Thunderbird < 60.8.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00010.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00001.html
- https://security.gentoo.org/glsa/201908-20
- https://www.mozilla.org/security/advisories/mfsa2019-21/
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00058.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00073.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00002.html
- https://security.gentoo.org/glsa/201908-12
- https://www.mozilla.org/security/advisories/mfsa2019-22/
- https://www.mozilla.org/security/advisories/mfsa2019-23/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1548306
