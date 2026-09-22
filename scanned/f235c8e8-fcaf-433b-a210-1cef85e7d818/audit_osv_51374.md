# [H] CVE-2021-29986

## Summary
Severity: High
Advisory: CVE-2021-29986
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-17
Source: https://osv.dev/vulnerability/CVE-2021-29986
Type: osv

## Details
A suspected race condition when calling getaddrinfo led to memory corruption and a potentially exploitable crash. *Note: This issue only affected Linux operating systems. Other operating systems are unaffected.* This vulnerability affects Thunderbird < 78.13, Thunderbird < 91, Firefox ESR < 78.13, and Firefox < 91.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-34/
- https://www.mozilla.org/security/advisories/mfsa2021-35/
- https://www.mozilla.org/security/advisories/mfsa2021-36/
- https://security.gentoo.org/glsa/202202-03
- https://security.gentoo.org/glsa/202208-14
- https://www.mozilla.org/security/advisories/mfsa2021-33/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1696138
