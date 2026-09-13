# [H] Code execution in metagpt

## Summary
Severity: High
Advisory: GHSA-g7ph-8423-pf4j
CVE: CVE-2024-23750
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-22
Source: https://github.com/advisories/GHSA-g7ph-8423-pf4j
Type: github-advisory

## Affected
- PyPI: `metagpt` — affected >=0

## Details
MetaGPT through 0.6.4 allows the QaEngineer role to execute arbitrary code because RunCode.run_script() passes shell metacharacters to subprocess.Popen.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23750
- https://github.com/geekan/MetaGPT/issues/731
- https://github.com/geekan/MetaGPT
- https://github.com/pypa/advisory-database/tree/main/vulns/metagpt/PYSEC-2024-9.yaml
