# [C] MLFlow path traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-vhcx-3pq2-4fvc
CVE: CVE-2025-15036
CWE: CWE-29
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-vhcx-3pq2-4fvc
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.9.0rc0

## Details
A path traversal vulnerability exists in the `extract_archive_to_dir` function within the `mlflow/pyfunc/dbconnect_artifact_cache.py` file of the mlflow/mlflow repository. This vulnerability, present in versions before v3.7.0, arises due to the lack of validation of tar member paths during extraction. An attacker with control over the tar.gz file can exploit this issue to overwrite arbitrary files or gain elevated privileges, potentially escaping the sandbox directory in multi-tenant or shared cluster environments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-15036
- https://github.com/mlflow/mlflow/commit/3bf6d81ac4d38654c8ff012dbd0c3e9f17e7e346
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/36c314cf-fd6e-4fb0-b9b0-1b47bcdf0eb0
