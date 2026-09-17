# [C] OS Command Injection in jw.util

## Summary
Severity: Critical
Advisory: GHSA-h72c-w3q3-55qq
CVE: CVE-2020-13388
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-02
Source: https://github.com/advisories/GHSA-h72c-w3q3-55qq
Type: github-advisory

## Affected
- PyPI: `jw.util` — affected >=0 <2.3

## Details
An exploitable vulnerability exists in the configuration-loading functionality of the jw.util package before 2.3 for Python. When loading a configuration with FromString or FromStream with YAML, one can execute arbitrary Python code, resulting in OS command execution, because safe_load is not used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13388
- https://joel-malwarebenchmark.github.io
- https://joel-malwarebenchmark.github.io/blog/2020/04/27/cve-2020-13388-jw-util-vulnerability
- https://security.netapp.com/advisory/ntap-20200528-0002
