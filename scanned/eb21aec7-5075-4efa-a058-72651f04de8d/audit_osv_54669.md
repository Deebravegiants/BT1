# [H] CVE-2024-2608

## Summary
Severity: High
Advisory: CVE-2024-2608
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-19
Source: https://osv.dev/vulnerability/CVE-2024-2608
Type: osv

## Details
`AppendEncodedAttributeValue(), ExtraSpaceNeededForAttrEncoding()` and `AppendEncodedCharacters()` could have experienced integer overflows, causing underallocation of an output buffer leading to an out of bounds write. This vulnerability affects Firefox < 124, Firefox ESR < 115.9, and Thunderbird < 115.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-12/
- https://www.mozilla.org/security/advisories/mfsa2024-13/
- https://www.mozilla.org/security/advisories/mfsa2024-14/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1880692
- https://lists.debian.org/debian-lts-announce/2024/03/msg00022.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00028.html
