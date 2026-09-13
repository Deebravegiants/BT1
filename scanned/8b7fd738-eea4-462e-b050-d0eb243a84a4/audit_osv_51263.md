# [M] CVE-2021-23973

## Summary
Severity: Medium
Advisory: CVE-2021-23973
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2021-23973
Type: osv

## Details
When trying to load a cross-origin resource in an audio/video context a decoding error may have resulted, and the content of that error may have revealed information about the resource. This vulnerability affects Firefox < 86, Thunderbird < 78.8, and Firefox ESR < 78.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-09/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00000.html
- https://security.gentoo.org/glsa/202104-09
- https://security.gentoo.org/glsa/202104-10
- https://www.debian.org/security/2021/dsa-4866
- https://www.mozilla.org/security/advisories/mfsa2021-07/
- https://www.mozilla.org/security/advisories/mfsa2021-08/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1690976
