# [M] CVE-2025-0238

## Summary
Severity: Medium
Advisory: CVE-2025-0238
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2025-0238
Type: osv

## Details
Assuming a controlled failed memory allocation, an attacker could have caused a use-after-free, leading to a potentially exploitable crash. This vulnerability affects Firefox < 134, Firefox ESR < 128.6, Firefox ESR < 115.19, Thunderbird < 134, and Thunderbird < 128.6.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00004.html
- https://www.mozilla.org/security/advisories/mfsa2025-03/
- https://www.mozilla.org/security/advisories/mfsa2025-04/
- https://www.mozilla.org/security/advisories/mfsa2025-05/
- https://www.mozilla.org/security/advisories/mfsa2025-01/
- https://www.mozilla.org/security/advisories/mfsa2025-02/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1915535
