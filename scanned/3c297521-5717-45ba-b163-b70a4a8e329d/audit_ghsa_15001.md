# [M] Remote Code Execution in create_conda_env function in lollms

## Summary
Severity: Medium
Advisory: GHSA-79h8-gxhq-q3jg
CVE: CVE-2024-3121
CWE: CWE-78, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-24
Source: https://github.com/advisories/GHSA-79h8-gxhq-q3jg
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0

## Details
A remote code execution vulnerability exists in the create_conda_env function of the parisneo/lollms repository. The vulnerability arises from the use of shell=True in the subprocess.Popen function, which allows an attacker to inject arbitrary commands by manipulating the env_name and python_version parameters. This issue could lead to a serious security breach as demonstrated by the ability to execute the 'whoami' command among potentially other harmful commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3121
- https://github.com/ParisNeo/lollms
- https://huntr.com/bounties/db57c343-9b80-4c1c-9ab0-9eef92c9b27b
