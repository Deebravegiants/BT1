# [H] CVE-2020-26971

## Summary
Severity: High
Advisory: CVE-2020-26971
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-01-07
Source: https://osv.dev/vulnerability/CVE-2020-26971
Type: osv

## Details
Certain blit values provided by the user were not properly constrained leading to a heap buffer overflow on some video drivers. This vulnerability affects Firefox < 84, Thunderbird < 78.6, and Firefox ESR < 78.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-54/
- https://www.mozilla.org/security/advisories/mfsa2020-55/
- https://www.mozilla.org/security/advisories/mfsa2020-56/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1663466
