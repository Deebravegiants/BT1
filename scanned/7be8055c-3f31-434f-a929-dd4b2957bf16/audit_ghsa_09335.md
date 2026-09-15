# [C] MLflow allows unauthorized access to multipart upload endpoints when the `--serve-artifacts` mode is enabled

## Summary
Severity: Critical
Advisory: GHSA-8c7q-86fq-vvmh
CVE: CVE-2026-2651
CWE: CWE-1220, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-8c7q-86fq-vvmh
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.11.0rc1

## Details
A vulnerability in MLflow versions <=3.10.1.dev0 allows unauthorized access to multipart upload (MPU) endpoints when the `--serve-artifacts` mode is enabled. The authorization logic does not enforce resource-level permission checks for `/mlflow-artifacts/mpu/*` endpoints, enabling attackers to overwrite artifacts belonging to other users. This can lead to unauthorized cross-user writes, model supply chain poisoning, and arbitrary code execution when compromised models are loaded. The issue is resolved in version 3.10.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2651
- https://github.com/mlflow/mlflow/commit/d7290811d8f3c95366d80109424edc1fb1ad966f
- https://access.redhat.com/security/cve/CVE-2026-2651
- https://bugzilla.redhat.com/show_bug.cgi?id=2481117
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/65beb119-d3e0-4e03-af2f-fa98f78f83dc
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-2651.json
