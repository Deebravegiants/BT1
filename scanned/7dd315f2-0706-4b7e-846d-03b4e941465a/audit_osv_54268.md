# [M] CVE-2023-4577

## Summary
Severity: Medium
Advisory: CVE-2023-4577
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-09-11
Source: https://osv.dev/vulnerability/CVE-2023-4577
Type: osv

## Details
When `UpdateRegExpStatics` attempted to access `initialStringHeap` it could already have been garbage collected prior to entering the function, which could potentially have led to an exploitable crash. This vulnerability affects Firefox < 117, Firefox ESR < 115.2, and Thunderbird < 115.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-38/
- https://www.mozilla.org/security/advisories/mfsa2023-34/
- https://www.mozilla.org/security/advisories/mfsa2023-36/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1847397
