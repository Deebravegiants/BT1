# [H] CVE-2024-8382

## Summary
Severity: High
Advisory: CVE-2024-8382
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-8382
Type: osv

## Details
Internal browser event interfaces were exposed to web content when privileged EventHandler listener callbacks ran for those events. Web content that tried to use those interfaces would not be able to use them with elevated privileges, but their presence would indicate certain browser features had been used, such as when a user opened the Dev Tools console. This vulnerability affects Firefox < 130, Firefox ESR < 128.2, Firefox ESR < 115.15, Thunderbird < 128.2, and Thunderbird < 115.15.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00025.html
- https://www.mozilla.org/security/advisories/mfsa2024-39/
- https://www.mozilla.org/security/advisories/mfsa2024-40/
- https://www.mozilla.org/security/advisories/mfsa2024-41/
- https://www.mozilla.org/security/advisories/mfsa2024-43/
- https://www.mozilla.org/security/advisories/mfsa2024-44/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1906744
