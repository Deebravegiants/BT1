# [C] Ansible Arbitrary Code Execution

## Summary
Severity: Critical
Advisory: GHSA-wqq5-c89p-3wc3
CVE: CVE-2014-4966
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wqq5-c89p-3wc3
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <1.6.7

## Details
Ansible before 1.6.7 does not prevent inventory data with "{{" and "lookup" substrings, and does not prevent remote data with "{{" substrings, which allows remote attackers to execute arbitrary code via (1) crafted lookup('pipe') calls or (2) crafted Jinja2 data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4966
- https://github.com/ansible/ansible/commit/62a1295a3e08cb6c3e9f1b2a1e6e5dcaeab32527
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-204.yaml
- http://www.ocert.org/advisories/ocert-2014-004.html
