# [H] CVE-2023-5724

## Summary
Severity: High
Advisory: CVE-2023-5724
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-5724
Type: osv

## Details
Drivers are not always robust to extremely large draw calls and in some cases this scenario could have led to a crash. This vulnerability affects Firefox < 119, Firefox ESR < 115.4, and Thunderbird < 115.4.1.

## References
- https://www.debian.org/security/2023/dsa-5535
- https://www.debian.org/security/2023/dsa-5538
- https://www.mozilla.org/security/advisories/mfsa2023-45/
- https://www.mozilla.org/security/advisories/mfsa2023-46/
- https://www.mozilla.org/security/advisories/mfsa2023-47/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00037.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00042.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1836705
