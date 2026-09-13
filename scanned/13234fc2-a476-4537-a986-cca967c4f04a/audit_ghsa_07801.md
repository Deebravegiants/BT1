# [C] MLflow Use of Default Password Authentication Bypass Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-gq3w-7jj3-x7gr
CVE: CVE-2026-2635
CWE: CWE-1393
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-21
Source: https://github.com/advisories/GHSA-gq3w-7jj3-x7gr
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.8.0rc0

## Details
This vulnerability allows remote attackers to bypass authentication on affected installations of MLflow. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the basic_auth.ini file. The file contains hard-coded default credentials. An attacker can leverage this vulnerability to bypass authentication and execute arbitrary code in the context of the administrator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2635
- https://github.com/mlflow/mlflow/pull/19260
- https://github.com/mlflow/mlflow/commit/5bf2ec2bd4222a18d78631183ac7f6b752afe8a4
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/releases/tag/v3.8.0rc0
- https://www.zerodayinitiative.com/advisories/ZDI-26-111
