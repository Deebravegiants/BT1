# [H] MLflow allows an unauthenticated remote attacker to read arbitrary files from the server's filesystem

## Summary
Severity: High
Advisory: GHSA-42h5-h8qh-vv9v
CVE: CVE-2026-2614
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-42h5-h8qh-vv9v
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.10.0

## Details
A vulnerability in the `_create_model_version()` handler of `mlflow/server/handlers.py` in mlflow/mlflow versions 3.9.0 and earlier allows an unauthenticated remote attacker to read arbitrary files from the server's filesystem. The issue arises when a `CreateModelVersion` request includes the tag `mlflow.prompt.is_prompt`, which bypasses source path validation. This enables an attacker to store an arbitrary local filesystem path as the model version source. The `get_model_version_artifact_handler()` function later uses this source to serve files without verifying the model version's prompt status, leading to a complete confidentiality compromise. This issue is fixed in version 3.10.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2614
- https://github.com/mlflow/mlflow/commit/6e801f4259d96804c73107315b24cef0f6aa115a
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/19380271-3fbf-4beb-987e-6fd7069c55e6
