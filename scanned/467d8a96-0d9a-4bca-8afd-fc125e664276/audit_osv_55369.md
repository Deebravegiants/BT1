# [C] CVE-2025-4083

## Summary
Severity: Critical
Advisory: CVE-2025-4083
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-04-29
Source: https://osv.dev/vulnerability/CVE-2025-4083
Type: osv

## Details
A process isolation vulnerability in Thunderbird stemmed from improper handling of javascript: URIs, which could allow content to execute in the top-level document's process instead of the intended frame, potentially enabling a sandbox escape. This vulnerability affects Firefox < 138, Firefox ESR < 128.10, Firefox ESR < 115.23, Thunderbird < 138, and Thunderbird < 128.10.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00024.html
- https://www.mozilla.org/security/advisories/mfsa2025-30/
- https://www.mozilla.org/security/advisories/mfsa2025-31/
- https://www.mozilla.org/security/advisories/mfsa2025-32/
- https://www.mozilla.org/security/advisories/mfsa2025-28/
- https://www.mozilla.org/security/advisories/mfsa2025-29/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1958350
