# [H] CVE-2021-23994

## Summary
Severity: High
Advisory: CVE-2021-23994
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-23994
Type: osv

## Details
A WebGL framebuffer was not initialized early enough, resulting in memory corruption and an out of bound write. This vulnerability affects Firefox ESR < 78.10, Thunderbird < 78.10, and Firefox < 88.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-14/
- https://www.mozilla.org/security/advisories/mfsa2021-15/
- https://www.mozilla.org/security/advisories/mfsa2021-16/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1699077
