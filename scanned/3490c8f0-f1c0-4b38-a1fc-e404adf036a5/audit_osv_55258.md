# [M] CVE-2025-1934

## Summary
Severity: Medium
Advisory: CVE-2025-1934
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/CVE-2025-1934
Type: osv

## Details
It was possible to interrupt the processing of a RegExp bailout and run additional JavaScript, potentially triggering garbage collection when the engine was not expecting it. This vulnerability affects Firefox < 136, Firefox ESR < 128.8, Thunderbird < 136, and Thunderbird < 128.8.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00006.html
- https://www.mozilla.org/security/advisories/mfsa2025-14/
- https://www.mozilla.org/security/advisories/mfsa2025-16/
- https://www.mozilla.org/security/advisories/mfsa2025-17/
- https://www.mozilla.org/security/advisories/mfsa2025-18/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1942881
