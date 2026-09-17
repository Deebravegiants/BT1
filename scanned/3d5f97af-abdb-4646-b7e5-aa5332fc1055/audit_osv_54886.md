# [H] CVE-2024-5696

## Summary
Severity: High
Advisory: CVE-2024-5696
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-06-11
Source: https://osv.dev/vulnerability/CVE-2024-5696
Type: osv

## Details
By manipulating the text in an `&lt;input&gt;` tag, an attacker could have caused corrupt memory leading to a potentially exploitable crash. This vulnerability affects Firefox < 127, Firefox ESR < 115.12, and Thunderbird < 115.12.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00010.html
- https://www.mozilla.org/security/advisories/mfsa2024-25/
- https://www.mozilla.org/security/advisories/mfsa2024-26/
- https://www.mozilla.org/security/advisories/mfsa2024-28/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1896555
