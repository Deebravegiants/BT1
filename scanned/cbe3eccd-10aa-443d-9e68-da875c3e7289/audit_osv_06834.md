# [H] Incomplete Fix for CVE-2025-10279: Insecure Temporary Directory Permissions in mlflow/mlflow

## Summary
Severity: High
Advisory: BIT-mlflow-2026-4137
Aliases: CVE-2026-4137, GHSA-f2m9-wcf4-cwwx, PYSEC-2026-2655
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-mlflow-2026-4137
Type: osv

## Affected
- Bitnami: `mlflow` — affected >=0 <3.11.0

## Details
In mlflow/mlflow versions prior to 3.11.0, the `get_or_create_nfs_tmp_dir()` function in `mlflow/utils/file_utils.py` creates temporary directories with world-writable permissions (0o777), and the `_create_model_downloading_tmp_dir()` function in `mlflow/pyfunc/__init__.py` creates directories with group-writable permissions (0o770). These insecure permissions allow local attackers to tamper with model artifacts, such as cloudpickle-serialized Python objects, and achieve arbitrary code execution when the tampered artifacts are deserialized via `cloudpickle.load()`. This vulnerability is particularly critical in environments with shared NFS mounts, such as Databricks, where NFS is enabled by default. The issue is a continuation of the vulnerability class addressed in CVE-2025-10279, which was only partially fixed.

## References
- https://github.com/mlflow/mlflow/commit/1dcbb0c2fbd1f446c328830e601ca13a28219b8a
- https://huntr.com/bounties/648dc30b-76c7-4433-86b8-f43d926fd8d6
- https://nvd.nist.gov/vuln/detail/CVE-2026-4137
