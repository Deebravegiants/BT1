# [C] OS Command Injection in cookiecutter

## Summary
Severity: Critical
Advisory: GHSA-f4q6-9qm4-h8j4
CVE: CVE-2022-24065
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-09
Source: https://github.com/advisories/GHSA-f4q6-9qm4-h8j4
Type: github-advisory

## Affected
- PyPI: `cookiecutter` — affected >=0 <2.1.1

## Details
The package cookiecutter before 2.1.1 is vulnerable to Command Injection via hg argument injection. When calling the cookiecutter function from Python code with the checkout parameter, it is passed to the hg checkout command in a way that additional flags can be set. The additional flags can be used to perform a command injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24065
- https://github.com/cookiecutter/cookiecutter/commit/fdffddb31fd2b46344dfa317531ff155e7999f77
- https://github.com/advisories/GHSA-f4q6-9qm4-h8j4
- https://github.com/cookiecutter/cookiecutter
- https://github.com/cookiecutter/cookiecutter/releases/tag/2.1.1
- https://github.com/pypa/advisory-database/tree/main/vulns/cookiecutter/PYSEC-2022-204.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G5TXC4JYTNGOUFMCXPZ6QKWEZN3URTAK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HQKWT7SGFDCUPPLDIELTN7FVTHWDL5YK
- https://snyk.io/vuln/SNYK-PYTHON-COOKIECUTTER-2414281
