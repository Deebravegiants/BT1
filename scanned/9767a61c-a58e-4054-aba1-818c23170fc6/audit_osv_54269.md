# [M] CVE-2023-4578

## Summary
Severity: Medium
Advisory: CVE-2023-4578
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-09-11
Source: https://osv.dev/vulnerability/CVE-2023-4578
Type: osv

## Details
When calling `JS::CheckRegExpSyntax` a Syntax Error could have been set which would end in calling `convertToRuntimeErrorAndClear`. A path in the function could attempt to allocate memory when none is available which would have caused a newly created Out of Memory exception to be mishandled as a Syntax Error. This vulnerability affects Firefox < 117, Firefox ESR < 115.2, and Thunderbird < 115.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-34/
- https://www.mozilla.org/security/advisories/mfsa2023-36/
- https://www.mozilla.org/security/advisories/mfsa2023-38/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1839007
