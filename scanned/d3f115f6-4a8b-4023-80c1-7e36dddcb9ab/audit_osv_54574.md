# [M] CVE-2024-11695

## Summary
Severity: Medium
Advisory: CVE-2024-11695
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-11695
Type: osv

## Details
A crafted URL containing Arabic script and whitespace characters could have hidden the true origin of the page, resulting in a potential spoofing attack. This vulnerability affects Firefox < 133, Firefox ESR < 128.5, Thunderbird < 133, and Thunderbird < 128.5.

## References
- https://lists.debian.org/debian-lts-announce/2024/11/msg00029.html
- https://www.mozilla.org/security/advisories/mfsa2024-64/
- https://www.mozilla.org/security/advisories/mfsa2024-67/
- https://www.mozilla.org/security/advisories/mfsa2024-68/
- https://www.mozilla.org/security/advisories/mfsa2024-63/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1925496
