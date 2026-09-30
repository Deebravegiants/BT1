# [H] Arbitrary file write via tar traversal in mlflow

## Summary
Severity: High
Advisory: GHSA-fhff-qmm8-h2fp
CVE: CVE-2025-15031
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-fhff-qmm8-h2fp
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.9.0rc0

## Details
A vulnerability in MLflow's pyfunc extraction process allows for arbitrary file writes due to improper handling of tar archive entries. Specifically, the use of `tarfile.extractall` without path validation enables crafted tar.gz files containing `..` or absolute paths to escape the intended extraction directory. This issue affects the latest version of MLflow and poses a high/critical risk in scenarios involving multi-tenant environments or ingestion of untrusted artifacts, as it can lead to arbitrary file overwrites and potential remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-15031
- https://github.com/mlflow/mlflow/commit/3bf6d81ac4d38654c8ff012dbd0c3e9f17e7e346
- https://github.com/mlflow/mlflow
- https://github.com/mlflow/mlflow/blob/fe4d9be330426904283401f1d2ed914238b6fc37/mlflow/pyfunc/dbconnect_artifact_cache.py#L140
- https://huntr.com/bounties/09856f77-f968-446f-a930-657d126efe4e
