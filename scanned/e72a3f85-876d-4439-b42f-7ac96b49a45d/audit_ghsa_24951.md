# [C] Unsafe pyyaml load usage in PyAnyAPI

## Summary
Severity: Critical
Advisory: GHSA-vg8g-jpm9-jh8r
CVE: CVE-2017-16616
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vg8g-jpm9-jh8r
Type: github-advisory

## Affected
- PyPI: `pyanyapi` — affected >=0 <0.6.1

## Details
An exploitable vulnerability exists in the YAML parsing functionality in the YAMLParser method in Interfaces.py in PyAnyAPI before 0.6.1. A YAML parser can execute arbitrary Python commands resulting in command execution because `load` is used where `safe_load` should have been used. An attacker can insert Python into loaded YAML to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16616
- https://github.com/Stranger6667/pyanyapi/issues/41
- https://github.com/Stranger6667/pyanyapi/commit/810db626c18ebc261d5f4299d0f0eac38d5eb3cf
- https://github.com/Stranger6667/pyanyapi
- https://github.com/Stranger6667/pyanyapi/releases/tag/0.6.1
- https://github.com/advisories/GHSA-vg8g-jpm9-jh8r
- https://github.com/pypa/advisory-database/tree/main/vulns/pyanyapi/PYSEC-2017-23.yaml
- https://joel-malwarebenchmark.github.io/blog/2017/11/08/cve-2017-16616-yamlparser-in-pyanyapi
- https://pypi.python.org/pypi/pyanyapi/0.6.1
