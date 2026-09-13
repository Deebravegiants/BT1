# [H] MLflow Tracking Server Artifact Handler Directory Traversal Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-q2r8-vmq7-fpx2
CVE: CVE-2026-2033
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-21
Source: https://github.com/advisories/GHSA-q2r8-vmq7-fpx2
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.8.0rc0

## Details
MLflow Tracking Server Artifact Handler Directory Traversal Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of MLflow Tracking Server. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the handling of artifact file paths. The issue results from the lack of proper validation of a user-supplied path prior to using it in file operations. An attacker can leverage this vulnerability to execute code in the context of the service account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2033
- https://github.com/mlflow/mlflow/pull/19260
- https://github.com/mlflow/mlflow/commit/5bf2ec2bd4222a18d78631183ac7f6b752afe8a4
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/releases/tag/v3.8.0rc0
- https://www.zerodayinitiative.com/advisories/ZDI-26-105
