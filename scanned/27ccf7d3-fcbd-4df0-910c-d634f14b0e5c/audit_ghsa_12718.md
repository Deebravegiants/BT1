# [C] himiklab yii2-jqgrid-widget vulnerable to SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-7mg5-rw39-q67f
CVE: CVE-2014-125051
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-7mg5-rw39-q67f
Type: github-advisory

## Affected
- Packagist: `himiklab/yii2-jqgrid-widget` — affected >=0 <1.0.8

## Details
A vulnerability was found in himiklab yii2-jqgrid-widget up to 1.0.7. It has been declared as critical. This vulnerability affects the function `addSearchOptionsRecursively` of the file `JqGridAction.php`. The manipulation leads to sql injection. Upgrading to version 1.0.8 can address this issue. The name of the patch is a117e0f2df729e3ff726968794d9a5ac40e660b9. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-217564.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-125051
- https://github.com/himiklab/yii2-jqgrid-widget/commit/a117e0f2df729e3ff726968794d9a5ac40e660b9
- https://github.com/himiklab/yii2-jqgrid-widget
- https://github.com/himiklab/yii2-jqgrid-widget/releases/tag/1.0.8
- https://vuldb.com/?ctiid.217564
- https://vuldb.com/?id.217564
