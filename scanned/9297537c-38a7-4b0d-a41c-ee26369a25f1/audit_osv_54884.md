# [M] CVE-2024-5691

## Summary
Severity: Medium
Advisory: CVE-2024-5691
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N)
Published: 2024-06-11
Source: https://osv.dev/vulnerability/CVE-2024-5691
Type: osv

## Details
By tricking the browser with a `X-Frame-Options` header, a sandboxed iframe could have presented a button that, if clicked by a user, would bypass restrictions to open a new window. This vulnerability affects Firefox < 127, Firefox ESR < 115.12, and Thunderbird < 115.12.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-25/
- https://www.mozilla.org/security/advisories/mfsa2024-26/
- https://www.mozilla.org/security/advisories/mfsa2024-28/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1888695
- https://lists.debian.org/debian-lts-announce/2024/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00010.html
