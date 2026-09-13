# [C] CVE-2025-8031

## Summary
Severity: Critical
Advisory: CVE-2025-8031
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-8031
Type: osv

## Details
The `username:password` part was not correctly stripped from URLs in CSP reports potentially leaking HTTP Basic Authentication credentials. This vulnerability affects Firefox < 141, Firefox ESR < 128.13, Firefox ESR < 140.1, Thunderbird < 141, Thunderbird < 128.13, and Thunderbird < 140.1.

## References
- https://lists.debian.org/debian-lts-announce/2025/07/msg00016.html
- https://www.mozilla.org/security/advisories/mfsa2025-56/
- https://www.mozilla.org/security/advisories/mfsa2025-58/
- https://www.mozilla.org/security/advisories/mfsa2025-59/
- https://www.mozilla.org/security/advisories/mfsa2025-61/
- https://www.mozilla.org/security/advisories/mfsa2025-62/
- https://www.mozilla.org/security/advisories/mfsa2025-63/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1971719
