# [H] MLflow Tracking Server Model Creation Directory Traversal Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-5cvj-7rg6-jggj
CVE: CVE-2025-11201
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-5cvj-7rg6-jggj
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=3.0.0rc0 <3.0.0
- PyPI: `mlflow` — affected >=0 <2.22.4

## Details
MLflow Tracking Server Model Creation Directory Traversal Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of MLflow Tracking Server. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the handling of model file paths. The issue results from the lack of proper validation of a user-supplied path prior to using it in file operations. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-26921.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11201
- https://github.com/B-Step62/mlflow/commit/2e02bc7bb70df243e6eb792689d9b8eba0013161
- https://github.com/mlflow/mlflow/commit/5f98ff98659dddb188591ecf6b10a4e276a0dba7
- https://github.com/mlflow/mlflow/commit/e7dc0574fa3459e0003cfeb68d4e4a625491f03d
- https://github.com/mlflow/mlflow
- https://www.zerodayinitiative.com/advisories/ZDI-25-931
