# [H] NextCRM has Broken Access Control in Server Actions that allows any authenticated user to deactivate/activate arbitrary accounts

## Summary
Severity: High
Advisory: CVE-2026-47129
Aliases: GHSA-gm7p-f88p-vhfr
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-47129
Type: osv

## Details
NextCRM is open-source customer relationship management (CRM) software. Versions prior to 0.12.0 have a Broken Access Control (BAC) vulnerability in the `activateUser` and `deactivateUser` Next.js Server Actions of NextCRM. The application fails to verify if the requesting user holds the `admin` role. Consequently, any authenticated user (even those with the lowest `member` or `viewer` roles) can arbitrarily activate or deactivate any user account in the system, including the main administrator. Version 0.12.0 fixes the issue.

## References
- https://github.com/pdovhomilja/nextcrm-app/releases/tag/v0.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47129.json
- https://github.com/pdovhomilja/nextcrm-app/security/advisories/GHSA-gm7p-f88p-vhfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-47129
