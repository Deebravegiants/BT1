# [M] NukeView CMS vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-x45f-j34v-75xm
CVE: CVE-2022-3975
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-13
Source: https://github.com/advisories/GHSA-x45f-j34v-75xm
Type: github-advisory

## Affected
- Packagist: `nukeviet/nukeviet` — affected >=0 <4.5

## Details
NukeView CMS has been found to be vulnerable to Cross-site Scripting. Affected by this issue is the function filterAttr of the file vendor/vinades/nukeviet/Core/Request.php of the component Data URL Handler. The manipulation of the argument attrSubSet leads to cross site scripting. The attack may be launched remotely. Upgrading to version 4.5 is able to address this issue. The name of the patch is 0b3197fad950bb3383e83039a8ee4c9509b3ce02. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3975
- https://github.com/nukeviet/nukeviet/commit/0b3197fad950bb3383e83039a8ee4c9509b3ce02
- https://github.com/nukeviet/nukeviet
- https://vuldb.com/?id.213554
