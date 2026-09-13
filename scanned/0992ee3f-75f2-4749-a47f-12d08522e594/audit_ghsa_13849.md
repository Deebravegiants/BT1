# [H] markdown-it-py Denial of Service vulnerability in the command line interface

## Summary
Severity: High
Advisory: GHSA-jrwr-5x3p-hvc3
CVE: CVE-2023-26302
CWE: CWE-173
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-23
Source: https://github.com/advisories/GHSA-jrwr-5x3p-hvc3
Type: github-advisory

## Affected
- PyPI: `markdown-it-py` — affected >=0 <2.2.0

## Details
Denial of service could be caused to the command line interface of markdown-it-py, before v2.2.0, if an attacker was allowed to use invalid UTF-8 characters as input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26302
- https://github.com/executablebooks/markdown-it-py/pull/247
- https://github.com/executablebooks/markdown-it-py/commit/53ca3e9c2b9e9b295f6abf7f4ad2730a9b70f68c
- https://github.com/executablebooks/markdown-it-py
- https://github.com/executablebooks/markdown-it-py/releases/tag/v2.2.0
- https://github.com/pypa/advisory-database/tree/main/vulns/markdown-it-py/PYSEC-2023-23.yaml
