# [H] CVE-2023-5728

## Summary
Severity: High
Advisory: CVE-2023-5728
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-5728
Type: osv

## Details
During garbage collection extra operations were performed on a object that should not be. This could have led to a potentially exploitable crash. This vulnerability affects Firefox < 119, Firefox ESR < 115.4, and Thunderbird < 115.4.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-46/
- https://www.mozilla.org/security/advisories/mfsa2023-47/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00037.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00042.html
- https://www.debian.org/security/2023/dsa-5535
- https://www.debian.org/security/2023/dsa-5538
- https://www.mozilla.org/security/advisories/mfsa2023-45/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1852729
