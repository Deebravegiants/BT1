# [H] CVE-2024-9400

## Summary
Severity: High
Advisory: CVE-2024-9400
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-10-01
Source: https://osv.dev/vulnerability/CVE-2024-9400
Type: osv

## Details
A potential memory corruption vulnerability could be triggered if an attacker had the ability to trigger an OOM at a specific moment during JIT compilation. This vulnerability affects Firefox < 131, Firefox ESR < 128.3, Thunderbird < 128.3, and Thunderbird < 131.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-46/
- https://www.mozilla.org/security/advisories/mfsa2024-47/
- https://www.mozilla.org/security/advisories/mfsa2024-49/
- https://www.mozilla.org/security/advisories/mfsa2024-50/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1915249
