# [M] CVE-2023-4581

## Summary
Severity: Medium
Advisory: CVE-2023-4581
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2023-09-11
Source: https://osv.dev/vulnerability/CVE-2023-4581
Type: osv

## Details
Excel `.xll` add-in files did not have a blocklist entry in Firefox's executable blocklist which allowed them to be downloaded without any warning of their potential harm. This vulnerability affects Firefox < 117, Firefox ESR < 102.15, Firefox ESR < 115.2, Thunderbird < 102.15, and Thunderbird < 115.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-35/
- https://www.mozilla.org/security/advisories/mfsa2023-36/
- https://www.mozilla.org/security/advisories/mfsa2023-37/
- https://www.mozilla.org/security/advisories/mfsa2023-38/
- https://www.mozilla.org/security/advisories/mfsa2023-34/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1843758
