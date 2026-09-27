# [C] CVE-2025-4918

## Summary
Severity: Critical
Advisory: CVE-2025-4918
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-17
Source: https://osv.dev/vulnerability/CVE-2025-4918
Type: osv

## Details
An attacker was able to perform an out-of-bounds read or write on a JavaScript `Promise` object. This vulnerability affects Firefox < 138.0.4, Firefox ESR < 128.10.1, Firefox ESR < 115.23.1, Thunderbird < 128.10.2, and Thunderbird < 138.0.2.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00046.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00024.html
- https://www.mozilla.org/security/advisories/mfsa2025-38/
- https://www.mozilla.org/security/advisories/mfsa2025-40/
- https://www.mozilla.org/security/advisories/mfsa2025-36/
- https://www.mozilla.org/security/advisories/mfsa2025-37/
- https://www.mozilla.org/security/advisories/mfsa2025-41/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1966612
- https://www.vicarius.io/vsociety/posts/cve-2025-4918-detect-firefox-out-of-bounds-write
- https://www.vicarius.io/vsociety/posts/cve-2025-4918-mitigate-firefox-out-of-bounds-write
