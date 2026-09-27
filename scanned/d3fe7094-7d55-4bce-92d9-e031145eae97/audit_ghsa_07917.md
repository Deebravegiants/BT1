# [H] mlflow Creates of Temporary File in Directory with Insecure Permissions

## Summary
Severity: High
Advisory: GHSA-4x5p-f36r-mxxr
CVE: CVE-2025-10279
CWE: CWE-379
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-4x5p-f36r-mxxr
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0 <3.4.0rc0

## Details
In mlflow version 2.20.3, the temporary directory used for creating Python virtual environments is assigned insecure world-writable permissions (0o777). This vulnerability allows an attacker with write access to the `/tmp` directory to exploit a race condition and overwrite `.py` files in the virtual environment, leading to arbitrary code execution. The issue is resolved in version 3.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10279
- https://github.com/mlflow/mlflow/commit/1d7c8d4cf0a67d407499a8a4ffac387ea4f8194a
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/01d3b81e-13d1-43aa-b91a-443aec68bdc8
