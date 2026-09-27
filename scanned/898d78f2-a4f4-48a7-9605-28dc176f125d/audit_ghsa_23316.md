# [C] Ansible Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-qg47-5px9-32g7
CVE: CVE-2014-4657
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qg47-5px9-32g7
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <1.5.4

## Details
The `safe_eval` function in Ansible before 1.5.4 does not properly restrict the code subset, which allows remote attackers to execute arbitrary code via crafted instructions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4657
- https://github.com/ansible/ansible/commit/998793fd0ab55705d57527a38cee5e83f535974c
- https://github.com/ansible/ansible
- https://github.com/ansible/ansible/blob/release1.5.5/CHANGELOG.md
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-199.yaml
- https://web.archive.org/web/20210120133852/https://www.securityfocus.com/bid/68232
