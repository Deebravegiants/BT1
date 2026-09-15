# [M] CVE-2024-3859

## Summary
Severity: Medium
Advisory: CVE-2024-3859
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-3859
Type: osv

## Details
On 32-bit versions there were integer-overflows that led to an out-of-bounds-read that potentially could be triggered by a malformed OpenType font. This vulnerability affects Firefox < 125, Firefox ESR < 115.10, and Thunderbird < 115.10.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/04/msg00013.html
- https://www.mozilla.org/security/advisories/mfsa2024-18/
- https://www.mozilla.org/security/advisories/mfsa2024-19/
- https://www.mozilla.org/security/advisories/mfsa2024-20/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1874489
