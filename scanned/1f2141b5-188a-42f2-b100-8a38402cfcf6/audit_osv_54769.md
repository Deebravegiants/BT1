# [H] CVE-2024-3854

## Summary
Severity: High
Advisory: CVE-2024-3854
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-3854
Type: osv

## Details
In some code patterns the JIT incorrectly optimized switch statements and generated code with out-of-bounds-reads. This vulnerability affects Firefox < 125, Firefox ESR < 115.10, and Thunderbird < 115.10.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00013.html
- https://www.mozilla.org/security/advisories/mfsa2024-18/
- https://www.mozilla.org/security/advisories/mfsa2024-19/
- https://www.mozilla.org/security/advisories/mfsa2024-20/
- https://lists.debian.org/debian-lts-announce/2024/04/msg00012.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1884552
