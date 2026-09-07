# [H] Apache Superset Improper Authorization allows low-privileged users to bypass access controls 

## Summary
Severity: High
Advisory: GHSA-3m2g-v7jf-7fxc
CVE: CVE-2026-23982
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-3m2g-v7jf-7fxc
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <6.0.0

## Details
An Improper Authorization vulnerability exists in Apache Superset that allows a low-privileged user to bypass data access controls. When creating a dataset, Superset enforces permission checks to prevent users from querying unauthorized data. However, an authenticated attacker with permissions to write datasets and read charts can bypass these checks by overwriting the SQL query of an existing dataset.

This issue affects Apache Superset: before 6.0.0.

Users are recommended to upgrade to version 6.0.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-23982
- https://github.com/apache/superset
- https://lists.apache.org/thread/9lvbzwkw4rxgdvbpfvnnnfcll92v75fp
- http://www.openwall.com/lists/oss-security/2026/02/24/6
