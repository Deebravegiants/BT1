# [C] CVE-2018-17181

## Summary
Severity: Critical
Advisory: CVE-2018-17181
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-17
Source: https://osv.dev/vulnerability/CVE-2018-17181
Type: osv

## Details
An issue was discovered in OpenEMR before 5.0.1 Patch 7. SQL Injection exists in the SaveAudit function in /portal/lib/paylib.php and the portalAudit function in /portal/lib/appsql.class.php.

## References
- https://github.com/openemr/openemr/commit/4963fe4932a0a4e1e982642226174e9931d09541
- https://www.open-emr.org/wiki/index.php/OpenEMR_Patches#5.0.1_Patch_.289.2F9.2F18.29
