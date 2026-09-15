# [C] Eve allows execution of arbitrary code

## Summary
Severity: Critical
Advisory: GHSA-8jxq-75rw-fhj9
CVE: CVE-2018-8097
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-8jxq-75rw-fhj9
Type: github-advisory

## Affected
- PyPI: `eve` — affected >=0 <0.7.5

## Details
`io/mongo/parser.py` in Eve (aka pyeve) before 0.7.5 allows remote attackers to execute arbitrary code via Code Injection in the `where` parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8097
- https://github.com/pyeve/eve/issues/1101
- https://github.com/pyeve/eve/commit/f8f7019ffdf9b4e05faf95e1f04e204aa4c91f98
- https://github.com/advisories/GHSA-8jxq-75rw-fhj9
- https://github.com/pyeve/eve
- https://github.com/pypa/advisory-database/tree/main/vulns/eve/PYSEC-2018-8.yaml
