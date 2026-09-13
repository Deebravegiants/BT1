# [C] Unsafe deserialization in MLAlchemy

## Summary
Severity: Critical
Advisory: GHSA-xpm8-98mx-h4c5
CVE: CVE-2017-16615
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-13
Source: https://github.com/advisories/GHSA-xpm8-98mx-h4c5
Type: github-advisory

## Affected
- PyPI: `MLAlchemy` — affected >=0 <0.2.2

## Details
An exploitable vulnerability exists in the YAML parsing functionality in the parse_yaml_query method in parser.py in MLAlchemy before 0.2.2. When processing YAML-Based queries for data, a YAML parser can execute arbitrary Python commands resulting in command execution because load is used where safe_load should have been used. An attacker can insert Python into loaded YAML to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16615
- https://github.com/thanethomson/MLAlchemy/issues/1
- https://github.com/thanethomson/MLAlchemy/commit/bc795757febdcce430d89f9d08f75c32d6989d3c
- https://github.com/pypa/advisory-database/tree/main/vulns/mlalchemy/PYSEC-2017-19.yaml
- https://github.com/thanethomson/MLAlchemy
- https://joel-malwarebenchmark.github.io/blog/2017/11/08/cve-2017-16615-critical-restful-web-applications-vulnerability
