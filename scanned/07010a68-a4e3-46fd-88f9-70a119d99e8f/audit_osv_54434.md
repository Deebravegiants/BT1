# [H] CVE-2023-6208

## Summary
Severity: High
Advisory: CVE-2023-6208
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-6208
Type: osv

## Details
When using X11, text selected by the page using the Selection API was erroneously copied into the primary selection, a temporary storage not unlike the clipboard.
*This bug only affects Firefox on X11. Other systems are unaffected.* This vulnerability affects Firefox < 120, Firefox ESR < 115.5.0, and Thunderbird < 115.5.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00030.html
- https://www.mozilla.org/security/advisories/mfsa2023-49/
- https://www.mozilla.org/security/advisories/mfsa2023-50/
- https://www.mozilla.org/security/advisories/mfsa2023-52/
- https://www.debian.org/security/2023/dsa-5561
- https://bugzilla.mozilla.org/show_bug.cgi?id=1855345
- https://lists.debian.org/debian-lts-announce/2023/11/msg00017.html
