# [M] Leantime affected by Improper Neutralization of HTML Tags

## Summary
Severity: Medium
Advisory: GHSA-95j3-435g-vjcp
CVE: CVE-2025-28254
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-02-21
Source: https://github.com/advisories/GHSA-95j3-435g-vjcp
Type: github-advisory

## Affected
- Packagist: `leantime/leantime` — affected >=0 <3.3

## Details
### Summary

HTML can be arbitrarily injected into emails from Leantime due to improper neutralization of HTML tags in users' first names. This effectively allows for the creation of phishing emails from a Leantime instance's email address.

## References
- https://github.com/Leantime/leantime/security/advisories/GHSA-95j3-435g-vjcp
- https://nvd.nist.gov/vuln/detail/CVE-2025-28254
- https://github.com/Leantime/leantime/commit/ce1d2073e4601183e1bdd90f4b433d16aee46a50
- https://github.com/Leantime/leantime
- https://github.com/Leantime/leantime/blob/0e7ddbbe3d582f657a1dddfef7b3419ae588cbf7/app/Domain/Notifications/Services/Notifications.php#L128
