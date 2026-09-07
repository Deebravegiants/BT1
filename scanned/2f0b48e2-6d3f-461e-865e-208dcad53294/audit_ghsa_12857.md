# [C] nodebatis SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8ph8-9q2j-c3rq
CVE: CVE-2018-25066
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-8ph8-9q2j-c3rq
Type: github-advisory

## Affected
- npm: `nodebatis` — affected >=0 <2.2.0

## Details
A vulnerability was found in PeterMu nodebatis up to 2.1.x. It has been classified as critical. Affected is an unknown function. The manipulation leads to sql injection. Upgrading to version 2.2.0 can address this issue. The name of the patch is 6629ff5b7e3d62ad8319007a54589ec1f62c7c35. It is recommended to upgrade the affected component. VDB-217554 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25066
- https://github.com/PeterMu/nodebatis/commit/6629ff5b7e3d62ad8319007a54589ec1f62c7c35
- https://github.com/PeterMu/nodebatis
- https://github.com/PeterMu/nodebatis/releases/tag/v2.2.0
- https://vuldb.com/?ctiid.217554
- https://vuldb.com/?id.217554
