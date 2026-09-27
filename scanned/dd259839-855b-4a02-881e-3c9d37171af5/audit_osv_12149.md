# [M] CVE-2018-10572

## Summary
Severity: Medium
Advisory: CVE-2018-10572
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-04-30
Source: https://osv.dev/vulnerability/CVE-2018-10572
Type: osv

## Details
interface/patient_file/letter.php in OpenEMR before 5.0.1 allows remote authenticated users to bypass intended access restrictions via the newtemplatename and form_body parameters.

## References
- https://www.open-emr.org/wiki/index.php/Release_Features#Version_5.0.1
- https://github.com/openemr/openemr/issues/1518
- https://github.com/openemr/openemr/pull/1519
- https://github.com/openemr/openemr/commit/699e3c2ef68545357cac714505df1419b8bf2051
- https://csticsfrontline.wordpress.com/2018/05/24/openemr-%E5%BC%B1%E9%BB%9E%E5%88%86%E6%9E%90/
