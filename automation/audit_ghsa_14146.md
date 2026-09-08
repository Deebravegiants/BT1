# [M] go package pydio cells vulnerable to cross-site scripting 

## Summary
Severity: Medium
Advisory: GHSA-wmfc-g86p-fjvr
CVE: CVE-2023-2981
CWE: CWE-80
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-30
Source: https://github.com/advisories/GHSA-wmfc-g86p-fjvr
Type: github-advisory

## Affected
- Go: `github.com/pydio/cells` — affected >=0 <4.2.1

## Details
A vulnerability, which was classified as problematic, has been found in Abstrium Pydio Cells 4.2.0. This issue affects some unknown processing of the component Chat. The manipulation leads to basic cross site scripting. The attack may be initiated remotely. Upgrading to version 4.2.1 is able to address this issue. It is recommended to upgrade the affected component. The identifier VDB-230213 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2981
- https://github.com/pydio/cells
- https://popalltheshells.medium.com/multiple-cves-affecting-pydio-cells-4-2-0-321e7e4712be
- https://pydio.com/en/community/releases/pydio-cells/pydio-cells-enterprise-421
- https://vuldb.com/?ctiid.230213
- https://vuldb.com/?id.230213
