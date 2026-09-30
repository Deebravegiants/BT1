# [C] Donfig Command Injection in collect_yaml method

## Summary
Severity: Critical
Advisory: GHSA-3qr5-h7w4-3gx3
CVE: CVE-2019-7537
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3qr5-h7w4-3gx3
Type: github-advisory

## Affected
- PyPI: `donfig` — affected >=0 <0.4.0

## Details
An issue was discovered in Donfig 0.3.0. There is a vulnerability in the `collect_yaml` method in `config_obj.py`. It can execute arbitrary Python commands, resulting in command execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7537
- https://github.com/pytroll/donfig/issues/5
- https://github.com/pytroll/donfig/commit/1f9dbf83b17419a06d63c14ef3fbd29dbc1b8ce5
- https://github.com/pypa/advisory-database/tree/main/vulns/donfig/PYSEC-2019-21.yaml
- https://github.com/pytroll/donfig
- https://github.com/pytroll/donfig/commits/master
