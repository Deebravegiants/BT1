# [M] CVE-2024-4767

## Summary
Severity: Medium
Advisory: CVE-2024-4767
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/CVE-2024-4767
Type: osv

## Details
If the `browser.privatebrowsing.autostart` preference is enabled, IndexedDB files were not properly deleted when the window was closed. This preference is disabled by default in Firefox. This vulnerability affects Firefox < 126, Firefox ESR < 115.11, and Thunderbird < 115.11.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-21/
- https://www.mozilla.org/security/advisories/mfsa2024-22/
- https://www.mozilla.org/security/advisories/mfsa2024-23/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1878577
- https://lists.debian.org/debian-lts-announce/2024/05/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/05/msg00010.html
