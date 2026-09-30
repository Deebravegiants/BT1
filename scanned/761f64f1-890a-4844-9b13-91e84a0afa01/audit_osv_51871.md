# [H] CVE-2021-43535

## Summary
Severity: High
Advisory: CVE-2021-43535
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-43535
Type: osv

## Details
A use-after-free could have occured when an HTTP2 session object was released on a different thread, leading to memory corruption and a potentially exploitable crash. This vulnerability affects Firefox < 93, Thunderbird < 91.3, and Firefox ESR < 91.3.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-49/
- https://www.mozilla.org/security/advisories/mfsa2021-50/
- https://lists.debian.org/debian-lts-announce/2021/12/msg00030.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://www.debian.org/security/2021/dsa-5026
- https://www.mozilla.org/security/advisories/mfsa2021-43/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1667102
- https://www.debian.org/security/2022/dsa-5034
