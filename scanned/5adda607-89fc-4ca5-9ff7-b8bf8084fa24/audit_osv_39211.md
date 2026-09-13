# [C] ChurchCRM: Incomplete fix for CVE-2026-40582: public API login still bypasses 2FA and account lockout in ChurchCRM 7.2.2

## Summary
Severity: Critical
Advisory: CVE-2026-44547
Aliases: GHSA-cwp8-rm8g-q5c9
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44547
Type: osv

## Details
ChurchCRM is an open-source church management system. From 7.2.0 to 7.2.2, The fix for CVE-2026-4058 is incomplete. The hardening commit was merged and then silently stripped from src/api/routes/public/public-user.php by an unrelated PR before any 7.2.x tag was cut. Every shipped 7.2.x release therefore remains exploitable by the PoC published with the original advisory. This vulnerability is fixed in 7.3.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44547.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-cwp8-rm8g-q5c9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44547
- https://github.com/ChurchCRM/CRM/pull/8855
