# [M] CVE-2023-4573

## Summary
Severity: Medium
Advisory: CVE-2023-4573
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-09-11
Source: https://osv.dev/vulnerability/CVE-2023-4573
Type: osv

## Details
When receiving rendering data over IPC `mStream` could have been destroyed when initialized, which could have led to a use-after-free causing a potentially exploitable crash. This vulnerability affects Firefox < 117, Firefox ESR < 102.15, Firefox ESR < 115.2, Thunderbird < 102.15, and Thunderbird < 115.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-38/
- https://www.mozilla.org/security/advisories/mfsa2023-34/
- https://www.mozilla.org/security/advisories/mfsa2023-35/
- https://www.mozilla.org/security/advisories/mfsa2023-36/
- https://www.mozilla.org/security/advisories/mfsa2023-37/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1846687
