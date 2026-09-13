# [H] Jupyter Notebook file bypasses sanitization, executes JavaScript

## Summary
Severity: High
Advisory: GHSA-6cwv-x26c-w2q4
CVE: CVE-2018-8768
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-6cwv-x26c-w2q4
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=0 <5.4.1

## Details
In Jupyter Notebook before 5.4.1, a maliciously forged notebook file can bypass sanitization to execute JavaScript in the notebook context. Specifically, invalid HTML is 'fixed' by jQuery after sanitization, making it dangerous.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8768
- https://github.com/jupyter/notebook
- https://github.com/pypa/advisory-database/tree/main/vulns/notebook/PYSEC-2018-57.yaml
- https://lists.debian.org/debian-lts-announce/2020/11/msg00033.html
- http://openwall.com/lists/oss-security/2018/03/15/2
