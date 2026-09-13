# [M] CVE-2024-7526

## Summary
Severity: Medium
Advisory: CVE-2024-7526
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-08-06
Source: https://osv.dev/vulnerability/CVE-2024-7526
Type: osv

## Details
ANGLE failed to initialize parameters which lead to reading from uninitialized memory. This could be leveraged to leak sensitive data from memory. This vulnerability affects Firefox < 129, Firefox ESR < 115.14, Firefox ESR < 128.1, Thunderbird < 128.1, and Thunderbird < 115.14.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-33/
- https://www.mozilla.org/security/advisories/mfsa2024-34/
- https://www.mozilla.org/security/advisories/mfsa2024-35/
- https://www.mozilla.org/security/advisories/mfsa2024-37/
- https://www.mozilla.org/security/advisories/mfsa2024-38/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1910306
