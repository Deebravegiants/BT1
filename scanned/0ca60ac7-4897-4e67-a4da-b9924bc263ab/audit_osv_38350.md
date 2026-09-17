# [H] ChurchCRM has a DDL SQL Injection in GroupPropsFormRowOps.php

## Summary
Severity: High
Advisory: CVE-2026-39318
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-39318
Type: osv

## Details
ChurchCRM is an open-source church management system. Versions prior to 7.1.0 have an SQL injection vulnerability in the endpoints `/GroupPropsFormRowOps.php`, `/PersonCustomFieldsRowOps.php`, and `/FamilyCustomFieldsRowOps.php`. A user has to be authenticated. For `ManageGroups` privileges have to be enabled and for the other two endpoints the attack has to be executed by an administrative user. These users can inject arbitrary SQL statements through the `Field` parameter and thus modify tables from the database.  This vulnerability is fixed in 7.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39318.json
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-8r53-w4r6-w62c
- https://github.com/ChurchCRM/CRM/security/advisories/GHSA-j3vj-59vv-h4rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-39318
