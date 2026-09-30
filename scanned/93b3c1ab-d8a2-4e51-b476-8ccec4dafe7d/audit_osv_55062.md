# [M] CVE-2025-0239

## Summary
Severity: Medium
Advisory: CVE-2025-0239
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2025-0239
Type: osv

## Details
When using Alt-Svc, ALPN did not properly validate certificates when the original server is redirecting to an insecure site. This vulnerability affects Firefox < 134, Firefox ESR < 128.6, Thunderbird < 134, and Thunderbird < 128.6.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00004.html
- https://www.mozilla.org/security/advisories/mfsa2025-02/
- https://www.mozilla.org/security/advisories/mfsa2025-04/
- https://www.mozilla.org/security/advisories/mfsa2025-05/
- https://www.mozilla.org/security/advisories/mfsa2025-01/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1929156
