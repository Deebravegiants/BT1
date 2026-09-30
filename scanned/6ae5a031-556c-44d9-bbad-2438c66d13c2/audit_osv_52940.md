# [M] CVE-2022-22742

## Summary
Severity: Medium
Advisory: CVE-2022-22742
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-22742
Type: osv

## Details
When inserting text while in edit mode, some characters might have lead to out-of-bounds memory access causing a potentially exploitable crash. This vulnerability affects Firefox ESR < 91.5, Firefox < 96, and Thunderbird < 91.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-03/
- https://www.mozilla.org/security/advisories/mfsa2022-01/
- https://www.mozilla.org/security/advisories/mfsa2022-02/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1739923
