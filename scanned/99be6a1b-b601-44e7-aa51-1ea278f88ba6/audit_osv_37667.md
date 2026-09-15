# [M] SuiteCRM: RecordHandler::getRecord() missing ACLAccess('view') check allows any authenticated user to read any record (IDOR)

## Summary
Severity: Medium
Advisory: CVE-2026-32697
Aliases: GHSA-9p9g-224x-6rmm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-32697
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Prior to versions 8.9.3, the `RecordHandler::getRecord()` method retrieves any record by module and ID without checking the current user's ACL view permission. The companion `saveRecord()` method correctly checks `$bean->ACLAccess('save')`, but `getRecord()` skips the equivalent `ACLAccess('view')` check. Version 8.9.3 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32697.json
- https://github.com/SuiteCRM/SuiteCRM-Core/security/advisories/GHSA-9p9g-224x-6rmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32697
