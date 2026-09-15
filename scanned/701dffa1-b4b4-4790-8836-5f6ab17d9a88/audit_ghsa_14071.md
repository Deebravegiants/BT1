# [M] Go package pydio/cells vulnerable to authorization bypass

## Summary
Severity: Medium
Advisory: GHSA-mv7x-27pc-8c96
CVE: CVE-2023-2978
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-30
Source: https://github.com/advisories/GHSA-mv7x-27pc-8c96
Type: github-advisory

## Affected
- Go: `github.com/pydio/cells` — affected >=0 <4.2.1

## Details
A vulnerability was found in Abstrium Pydio Cells 4.2.0. It has been rated as problematic. Affected by this issue is some unknown functionality of the component Change Subscription Handler. The manipulation leads to authorization bypass. Upgrading to version 4.2.1 is able to address this issue. It is recommended to upgrade the affected component. VDB-230210 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2978
- https://popalltheshells.medium.com/multiple-cves-affecting-pydio-cells-4-2-0-321e7e4712be
- https://pydio.com/en/community/releases/pydio-cells/pydio-cells-enterprise-421
- https://vuldb.com/?ctiid.230210
- https://vuldb.com/?id.230210
- github.com/pydio/cells
