# [H] CVE-2020-26960

## Summary
Severity: High
Advisory: CVE-2020-26960
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-26960
Type: osv

## Details
If the Compact() method was called on an nsTArray, the array could have been reallocated without updating other pointers, leading to a potential use-after-free and exploitable crash. This vulnerability affects Firefox < 83, Firefox ESR < 78.5, and Thunderbird < 78.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-50/
- https://www.mozilla.org/security/advisories/mfsa2020-51/
- https://www.mozilla.org/security/advisories/mfsa2020-52/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1670358
