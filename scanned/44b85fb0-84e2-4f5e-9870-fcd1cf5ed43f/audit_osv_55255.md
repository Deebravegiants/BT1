# [H] CVE-2025-1931

## Summary
Severity: High
Advisory: CVE-2025-1931
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/CVE-2025-1931
Type: osv

## Details
It was possible to cause a use-after-free in the content process side of a WebTransport connection, leading to a potentially exploitable crash. This vulnerability affects Firefox < 136, Firefox ESR < 115.21, Firefox ESR < 128.8, Thunderbird < 136, and Thunderbird < 128.8.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00006.html
- https://www.mozilla.org/security/advisories/mfsa2025-17/
- https://www.mozilla.org/security/advisories/mfsa2025-18/
- https://www.mozilla.org/security/advisories/mfsa2025-14/
- https://www.mozilla.org/security/advisories/mfsa2025-15/
- https://www.mozilla.org/security/advisories/mfsa2025-16/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1944126
