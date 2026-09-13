# [C] CVE-2024-7519

## Summary
Severity: Critical
Advisory: CVE-2024-7519
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-08-06
Source: https://osv.dev/vulnerability/CVE-2024-7519
Type: osv

## Details
Insufficient checks when processing graphics shared memory could have led to memory corruption. This could be leveraged by an attacker to perform a sandbox escape. This vulnerability affects Firefox < 129, Firefox ESR < 115.14, Firefox ESR < 128.1, Thunderbird < 128.1, and Thunderbird < 115.14.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-37/
- https://www.mozilla.org/security/advisories/mfsa2024-38/
- https://www.mozilla.org/security/advisories/mfsa2024-33/
- https://www.mozilla.org/security/advisories/mfsa2024-34/
- https://www.mozilla.org/security/advisories/mfsa2024-35/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1902307
