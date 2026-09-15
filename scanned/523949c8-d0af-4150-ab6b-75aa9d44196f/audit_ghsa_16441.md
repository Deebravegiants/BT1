# [M] MLflow allows low privilege users to delete any artifact

## Summary
Severity: Medium
Advisory: GHSA-p4jx-q62p-x5jr
CVE: CVE-2024-4263
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-05-16
Source: https://github.com/advisories/GHSA-p4jx-q62p-x5jr
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <2.10.1

## Details
A broken access control vulnerability exists in mlflow/mlflow versions before 2.10.1, where low privilege users with only EDIT permissions on an experiment can delete any artifacts. This issue arises due to the lack of proper validation for DELETE requests by users with EDIT permissions, allowing them to perform unauthorized deletions of artifacts. The vulnerability specifically affects the handling of artifact deletions within the application, as demonstrated by the ability of a low privilege user to delete a directory inside an artifact using a DELETE request, despite the official documentation stating that users with EDIT permission can only read and update artifacts, not delete them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4263
- https://github.com/mlflow/mlflow/commit/b43e0e3de5b500554e13dc032ba2083b2d6c94b8
- https://github.com/mlflow/mlflow
- https://github.com/pypa/advisory-database/tree/main/vulns/mlflow/PYSEC-2024-51.yaml
- https://huntr.com/bounties/bfa116d3-2af8-4c4a-ac34-ccde7491ae11
