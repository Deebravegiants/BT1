# [H] NextCRM has a BOLA/IDOR in PATCH /api/crm/contacts/[id] that allows Cross-Tenant CRM Data Tampering

## Summary
Severity: High
Advisory: CVE-2026-47130
Aliases: GHSA-mg5f-m89f-4gmc
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-47130
Type: osv

## Details
NextCRM is open-source customer relationship management (CRM) software. Versions prior to 0.12.0 have a Broken Object Level Authorization (BOLA/IDOR) vulnerability exists in the CRM contact and target update endpoints. The application fails to verify if the authenticated user has ownership of the specific resource being modified. This allows any authenticated user (even with a standard `member` role) to arbitrarily modify sensitive CRM contacts and targets belonging to other users or organizations (cross-tenant data tampering). Version 0.12.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47130.json
- https://github.com/pdovhomilja/nextcrm-app/security/advisories/GHSA-mg5f-m89f-4gmc
- https://nvd.nist.gov/vuln/detail/CVE-2026-47130
