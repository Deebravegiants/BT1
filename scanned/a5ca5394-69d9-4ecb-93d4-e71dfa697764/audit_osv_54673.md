# [H] CVE-2024-2612

## Summary
Severity: High
Advisory: CVE-2024-2612
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-19
Source: https://osv.dev/vulnerability/CVE-2024-2612
Type: osv

## Details
If an attacker could find a way to trigger a particular code path in `SafeRefPtr`, it could have triggered a crash or potentially be leveraged to achieve code execution. This vulnerability affects Firefox < 124, Firefox ESR < 115.9, and Thunderbird < 115.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-13/
- https://www.mozilla.org/security/advisories/mfsa2024-14/
- https://www.mozilla.org/security/advisories/mfsa2024-12/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1879444
- https://lists.debian.org/debian-lts-announce/2024/03/msg00022.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00028.html
