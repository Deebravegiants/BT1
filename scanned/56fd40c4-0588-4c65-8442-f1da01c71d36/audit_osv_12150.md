# [H] CVE-2018-10573

## Summary
Severity: High
Advisory: CVE-2018-10573
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-30
Source: https://osv.dev/vulnerability/CVE-2018-10573
Type: osv

## Details
interface/fax/fax_dispatch.php in OpenEMR before 5.0.1 allows remote authenticated users to bypass intended access restrictions via the scan parameter.

## References
- https://www.open-emr.org/wiki/index.php/Release_Features#Version_5.0.1
- https://github.com/openemr/openemr/issues/1518
- https://github.com/openemr/openemr/commit/699e3c2ef68545357cac714505df1419b8bf2051
- https://github.com/openemr/openemr/pull/1519
- https://csticsfrontline.wordpress.com/2018/05/24/openemr-%E5%BC%B1%E9%BB%9E%E5%88%86%E6%9E%90/
