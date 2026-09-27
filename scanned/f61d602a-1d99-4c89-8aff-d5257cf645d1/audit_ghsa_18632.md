# [H] MLflow Weak Password Requirements Authentication Bypass Vulnerability

## Summary
Severity: High
Advisory: GHSA-6xj8-rrqx-r4cv
CVE: CVE-2025-11200
CWE: CWE-521
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-6xj8-rrqx-r4cv
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <2.22.0rc0

## Details
MLflow Weak Password Requirements Authentication Bypass Vulnerability. This vulnerability allows remote attackers to bypass authentication on affected installations of MLflow. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the handling of passwords. The issue results from weak password requirements. An attacker can leverage this vulnerability to bypass authentication on the system. Was ZDI-CAN-26916.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11200
- https://github.com/mlflow/mlflow/commit/1f74f3f24d8273927b8db392c23e108576936c54
- https://github.com/mlflow/mlflow
- https://www.zerodayinitiative.com/advisories/ZDI-25-932
