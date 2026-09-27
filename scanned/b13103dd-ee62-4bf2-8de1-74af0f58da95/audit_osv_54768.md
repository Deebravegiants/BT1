# [H] CVE-2024-3852

## Summary
Severity: High
Advisory: CVE-2024-3852
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-3852
Type: osv

## Details
GetBoundName could return the wrong version of an object when JIT optimizations were applied. This vulnerability affects Firefox < 125, Firefox ESR < 115.10, and Thunderbird < 115.10.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-18/
- https://www.mozilla.org/security/advisories/mfsa2024-19/
- https://www.mozilla.org/security/advisories/mfsa2024-20/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1883542
- https://lists.debian.org/debian-lts-announce/2024/04/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/04/msg00013.html
