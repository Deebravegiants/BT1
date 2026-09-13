# [M] CVE-2025-26695

## Summary
Severity: Medium
Advisory: CVE-2025-26695
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-03-10
Source: https://osv.dev/vulnerability/CVE-2025-26695
Type: osv

## Details
When requesting an OpenPGP key from a WKD server, an incorrect padding size was used and a network observer could have learned the length of the requested email address. This vulnerability affects Thunderbird < 136 and Thunderbird < 128.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2025-17/
- https://www.mozilla.org/security/advisories/mfsa2025-18/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1883039
