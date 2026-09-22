# [H] tree-kit vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-mw4x-g2x8-qcvf
CVE: CVE-2021-4278
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-25
Source: https://github.com/advisories/GHSA-mw4x-g2x8-qcvf
Type: github-advisory

## Affected
- npm: `tree-kit` — affected >=0 <0.7.0

## Details
A vulnerability classified as problematic has been found in cronvel tree-kit up to 0.6.x. This affects an unknown part. The manipulation leads to improperly controlled modification of object prototype attributes ('prototype pollution'). Upgrading to version 0.7.0 is able to address this issue. The name of the patch is a63f559c50d70e8cb2eaae670dec25d1dbc4afcd. It is recommended to upgrade the affected component. The identifier VDB-216765 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4278
- https://github.com/cronvel/tree-kit/commit/a63f559c50d70e8cb2eaae670dec25d1dbc4afcd
- https://github.com/cronvel/tree-kit
- https://github.com/cronvel/tree-kit/releases/tag/v0.7.0
- https://vuldb.com/?ctiid.216765
- https://vuldb.com/?id.216765
