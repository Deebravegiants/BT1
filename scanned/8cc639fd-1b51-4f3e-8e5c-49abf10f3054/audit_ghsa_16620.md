# [M] rockhopper Buffer Overflow vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4r4c-66gf-g9g5
CVE: CVE-2022-4969
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-4r4c-66gf-g9g5
Type: github-advisory

## Affected
- PyPI: `rockhopper` — affected >=0 <0.2.0

## Details
A vulnerability, which was classified as critical, has been found in bwoodsend rockhopper up to 0.1.2. Affected by this issue is the function `count_rows` of the file `rockhopper/src/ragged_array.c` of the component Binary Parser. The manipulation of the argument raw leads to buffer overflow. Local access is required to approach this attack. Upgrading to version 0.2.0 is able to address this issue. The name of the patch is 1a15fad5e06ae693eb9b8908363d2c8ef455104e. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-266312.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4969
- https://github.com/bwoodsend/rockhopper/commit/1a15fad5e06ae693eb9b8908363d2c8ef455104e
- https://github.com/bwoodsend/rockhopper
- https://github.com/bwoodsend/rockhopper/releases/tag/v0.2.0
- https://vuldb.com/?ctiid.266312
- https://vuldb.com/?id.266312
