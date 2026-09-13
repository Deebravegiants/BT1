# [H] Alkacon OpenCMS CSV Injection via New User module

## Summary
Severity: High
Advisory: GHSA-q693-v7qf-p4xj
CVE: CVE-2019-11819
CWE: CWE-1236
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q693-v7qf-p4xj
Type: github-advisory

## Affected
- Maven: `org.opencms:opencms-core` — affected >=0 <11.0.0

## Details
Alkacon OpenCMS v10.5.4 and before is affected by CSV (aka Excel Macro) Injection in the module New User (/opencms/system/workplace/admin/accounts/user_new.jsp) via the First Name or Last Name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11819
- https://github.com/alkacon/opencms-core/issues/636
- https://github.com/alkacon/opencms-core
- https://www.openwall.com/lists/oss-security/2019/05/05/2
