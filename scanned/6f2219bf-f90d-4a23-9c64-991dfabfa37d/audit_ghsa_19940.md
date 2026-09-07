# [M] Harvest Chosen vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-x5q4-m45m-fm94
CVE: CVE-2018-25050
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-x5q4-m45m-fm94
Type: github-advisory

## Affected
- Packagist: `harvesthq/chosen` — affected >=0 <1.8.7

## Details
A vulnerability, which was classified as problematic, has been found in Harvest Chosen up to 1.8.6. Affected by this issue is the function AbstractChosen of the file coffee/lib/abstract-chosen.coffee. The manipulation of the argument group_label leads to cross site scripting. The attack may be launched remotely. Upgrading to version 1.8.7 can address this issue. The name of the patch is 77fd031d541e77510268d1041ed37798fdd1017e. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-216956.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25050
- https://github.com/harvesthq/chosen/pull/2997
- https://github.com/harvesthq/chosen/commit/77fd031d541e77510268d1041ed37798fdd1017e
- https://github.com/harvesthq/chosen
- https://github.com/harvesthq/chosen/releases/tag/v1.8.7
- https://vuldb.com/?ctiid.216956
- https://vuldb.com/?id.216956
