# [M] LIEF contains a segmentation violation

## Summary
Severity: Medium
Advisory: GHSA-2p5h-hpj4-fxgg
CVE: CVE-2022-38497
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-14
Source: https://github.com/advisories/GHSA-2p5h-hpj4-fxgg
Type: github-advisory

## Affected
- PyPI: `lief` — affected >=0

## Details
LIEF commit 365a16a was discovered to contain a segmentation violation via the component `CoreFile.tcc:69`. A patch is available at commit ca938740264f1fcb18f91cba8e4039c518ecb75b.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38497
- https://github.com/lief-project/LIEF/issues/766
- https://github.com/lief-project/LIEF/commit/ca938740264f1fcb18f91cba8e4039c518ecb75b
- https://github.com/lief-project/LIEF
- https://github.com/pypa/advisory-database/tree/main/vulns/lief/PYSEC-2022-277.yaml
