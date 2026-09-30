# [C] DBRisinajumi d2files SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-68hv-8926-j34c
CVE: CVE-2015-10018
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-68hv-8926-j34c
Type: github-advisory

## Affected
- Packagist: `dbrisinajumi/d2files` — affected >=0 <1.0.0

## Details
A vulnerability has been found in DBRisinajumi d2files and classified as critical. Affected by this vulnerability is the function `actionUpload/actionDownloadFile` of the file `controllers/D2filesController.php`. The manipulation leads to sql injection. Upgrading to version 1.0.0 can address this issue. The name of the patch is b5767f2ec9d0f3cbfda7f13c84740e2179c90574. It is recommended to upgrade the affected component. The identifier VDB-217561 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-10018
- https://github.com/DBRisinajumi/d2files/commit/b5767f2ec9d0f3cbfda7f13c84740e2179c90574
- https://github.com/DBRisinajumi/d2files
- https://github.com/DBRisinajumi/d2files/releases/tag/1.0.0
- https://vuldb.com/?ctiid.217561
- https://vuldb.com/?id.217561
