# [H] CVE-2025-1011

## Summary
Severity: High
Advisory: CVE-2025-1011
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-02-04
Source: https://osv.dev/vulnerability/CVE-2025-1011
Type: osv

## Details
A bug in WebAssembly code generation could have lead to a crash. It may have been possible for an attacker to leverage this to achieve code execution. This vulnerability affects Firefox < 135, Firefox ESR < 128.7, Thunderbird < 128.7, and Thunderbird < 135.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00006.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00005.html
- https://www.mozilla.org/security/advisories/mfsa2025-07/
- https://www.mozilla.org/security/advisories/mfsa2025-09/
- https://www.mozilla.org/security/advisories/mfsa2025-10/
- https://www.mozilla.org/security/advisories/mfsa2025-11/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1936454
