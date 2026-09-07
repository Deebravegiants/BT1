# [C] mlflow: FastAPI job endpoints under `/ajax-api/3.0/jobs/*` are not protected by authentication or authorization

## Summary
Severity: Critical
Advisory: GHSA-7qhf-v65m-g5f3
CVE: CVE-2026-0545
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-7qhf-v65m-g5f3
Type: github-advisory

## Affected
- PyPI: `mlflow` — affected >=0

## Details
In mlflow/mlflow, the FastAPI job endpoints under `/ajax-api/3.0/jobs/*` are not protected by authentication or authorization when the `basic-auth` app is enabled. This vulnerability affects the latest version of the repository. If job execution is enabled (`MLFLOW_SERVER_ENABLE_JOB_EXECUTION=true`) and any job function is allowlisted, any network client can submit, read, search, and cancel jobs without credentials, bypassing basic-auth entirely. This can lead to unauthenticated remote code execution if allowed jobs perform privileged actions such as shell execution or filesystem changes. Even if jobs are deemed safe, this still constitutes an authentication bypass, potentially resulting in job spam, denial of service (DoS), or data exposure in job results.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0545
- https://github.com/mlflow/mlflow
- https://huntr.com/bounties/b2e5b028-9541-4d29-8703-a76f1a3734d8
