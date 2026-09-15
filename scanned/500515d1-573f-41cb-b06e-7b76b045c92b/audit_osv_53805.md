# [M] CVE-2023-25752

## Summary
Severity: Medium
Advisory: CVE-2023-25752
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-25752
Type: osv

## Details
When accessing throttled streams, the count of available bytes needed to be checked in the calling function to be within bounds. This may have lead future code to be incorrect and vulnerable. This vulnerability affects Firefox < 111, Firefox ESR < 102.9, and Thunderbird < 102.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-09/
- https://www.mozilla.org/security/advisories/mfsa2023-10/
- https://www.mozilla.org/security/advisories/mfsa2023-11/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1811627
