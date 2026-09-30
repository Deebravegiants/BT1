# [M] Abstrium Pydio Cells Resource Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j327-c69h-4gh8
CVE: CVE-2023-2980
CWE: CWE-74, CWE-99
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-05-30
Source: https://github.com/advisories/GHSA-j327-c69h-4gh8
Type: github-advisory

## Affected
- Go: `github.com/pydio/cells/v4` — affected >=0 <4.2.1

## Details
A vulnerability classified as critical was found in Abstrium Pydio Cells 4.2.0. This vulnerability affects unknown code of the component User Creation Handler. The manipulation leads to improper control of resource identifiers. The attack can be initiated remotely. Upgrading to version 4.2.1 is able to address this issue. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-230212.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2980
- https://github.com/pydio/cells
- https://popalltheshells.medium.com/multiple-cves-affecting-pydio-cells-4-2-0-321e7e4712be
- https://pydio.com/en/community/releases/pydio-cells/pydio-cells-enterprise-421
- https://vuldb.com/?ctiid.230212
- https://vuldb.com/?id.230212
