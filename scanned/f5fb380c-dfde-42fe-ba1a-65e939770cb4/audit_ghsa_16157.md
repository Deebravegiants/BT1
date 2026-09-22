# [H] virtualenv allows command injection through activation scripts for a virtual environment

## Summary
Severity: High
Advisory: GHSA-rqc4-2hc7-8c8v
CVE: CVE-2024-53899
CWE: CWE-77, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-24
Source: https://github.com/advisories/GHSA-rqc4-2hc7-8c8v
Type: github-advisory

## Affected
- PyPI: `virtualenv` — affected >=0 <20.26.6

## Details
virtualenv before 20.26.6 allows command injection through the activation scripts for a virtual environment. Magic template strings are not quoted correctly when replacing. NOTE: this is not the same as CVE-2024-9287.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53899
- https://github.com/pypa/virtualenv/issues/2768
- https://github.com/pypa/virtualenv/pull/2771
- https://github.com/pypa/advisory-database/tree/main/vulns/virtualenv/PYSEC-2024-187.yaml
- https://github.com/pypa/virtualenv
- https://github.com/pypa/virtualenv/releases/tag/20.26.6
