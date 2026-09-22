# [H] CVE-2024-5688

## Summary
Severity: High
Advisory: CVE-2024-5688
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-11
Source: https://osv.dev/vulnerability/CVE-2024-5688
Type: osv

## Details
If a garbage collection was triggered at the right time, a use-after-free could have occurred during object transplant. This vulnerability affects Firefox < 127, Firefox ESR < 115.12, and Thunderbird < 115.12.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00010.html
- https://www.mozilla.org/security/advisories/mfsa2024-25/
- https://www.mozilla.org/security/advisories/mfsa2024-26/
- https://www.mozilla.org/security/advisories/mfsa2024-28/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1895086
