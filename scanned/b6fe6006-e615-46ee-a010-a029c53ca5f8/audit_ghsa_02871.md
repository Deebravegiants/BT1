# [M] Code Injection in SLO Generator

## Summary
Severity: Medium
Advisory: GHSA-j28r-j54m-gpc4
CVE: CVE-2021-22557
CWE: CWE-78, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-10-05
Source: https://github.com/advisories/GHSA-j28r-j54m-gpc4
Type: github-advisory

## Affected
- PyPI: `slo-generator` — affected >=0 <2.0.1

## Details
SLO generator allows for loading of YAML files that if crafted in a specific format can allow for code execution within the context of the SLO Generator. We recommend upgrading SLO Generator past https://github.com/google/slo-generator/pull/173

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22557
- https://github.com/google/slo-generator/pull/173
- https://github.com/google/slo-generator/commit/36318beab1b85d14bb860e45bea186b184690d5d
- https://github.com/google/slo-generator/releases/tag/v2.0.1
- https://github.com/pypa/advisory-database/tree/main/vulns/slo-generator/PYSEC-2021-429.yaml
- ://github.com/google/slo-generator
- http://packetstormsecurity.com/files/164426/Google-SLO-Generator-2.0.0-Code-Execution.html
