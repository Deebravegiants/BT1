# [H] CVE-2024-6603

## Summary
Severity: High
Advisory: CVE-2024-6603
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2024-6603
Type: osv

## Details
In an out-of-memory scenario an allocation could fail but free would have been called on the pointer afterwards leading to memory corruption. This vulnerability affects Firefox < 128, Firefox ESR < 115.13, Thunderbird < 115.13, and Thunderbird < 128.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-29/
- https://www.mozilla.org/security/advisories/mfsa2024-30/
- https://www.mozilla.org/security/advisories/mfsa2024-31/
- https://www.mozilla.org/security/advisories/mfsa2024-32/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1895081
