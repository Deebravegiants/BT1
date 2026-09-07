# [C] Remote Code Execution due to Full Controled File Write in mlflow

## Summary
Severity: Critical
Advisory: GHSA-5p3h-7fwh-92rc
CVE: CVE-2023-6018
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-5p3h-7fwh-92rc
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <2.9.2

## Details
The mlflow web server includes tools for tracking experiments, packaging code into reproducible runs, and sharing and deploying models. As this vulnerability allows to write / overwrite any file on the file system, it gives a lot of ways to archive code execution (like overwriting `/home/<user>/.bashrc`). A malicious user could use this issue to get command execution on the vulnerable machine and get access to data & models information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6018
- https://github.com/mlflow/mlflow/commit/55c72d02380e8db8118595a4fdae7879cb7ac5bd
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/7cf918b5-43f4-48c0-a371-4d963ce69b30
