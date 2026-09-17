# [H] cocagne pysrp vulnerable to side channel leaks

## Summary
Severity: High
Advisory: GHSA-xmc3-9m9j-w9x4
CVE: CVE-2021-4286
CWE: CWE-203
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-xmc3-9m9j-w9x4
Type: github-advisory

## Affected
- PyPI: `srp` — affected >=0 <1.0.17

## Details
A vulnerability, which was classified as problematic, has been found in cocagne pysrp up to 1.0.16. This issue affects the function calculate_x of the file `srp/_ctsrp.py`. The manipulation leads to information exposure through discrepancy. Upgrading to version 1.0.17 is able to address this issue. The name of the patch is dba52642f5e95d3da7af1780561213ee6053195f. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-216875.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4286
- https://github.com/cocagne/pysrp/pull/43
- https://github.com/cocagne/pysrp/commit/dba52642f5e95d3da7af1780561213ee6053195f
- https://github.com/cocagne/pysrp
- https://github.com/cocagne/pysrp/releases/tag/1.0.17
- https://github.com/pypa/advisory-database/tree/main/vulns/srp/PYSEC-2022-43014.yaml
- https://vuldb.com/?ctiid.216875
- https://vuldb.com/?id.216875
