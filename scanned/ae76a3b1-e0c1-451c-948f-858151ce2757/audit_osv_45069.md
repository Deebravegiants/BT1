# [M] PYSEC-2025-17

## Summary
Severity: Medium
Advisory: PYSEC-2025-17
Aliases: BIT-mlflow-2025-1474, CVE-2025-1474, GHSA-4rj2-9gcx-5qhx
Ecosystem: PyPI
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/PYSEC-2025-17
Type: osv

## Affected
- PyPI: `mlflow` — affected >=0 <149c9e18aa219bc47e86b432e130e467a36f4a17, >=0 <2.19.0

## Details
In mlflow/mlflow version 2.18, an admin is able to create a new user account without setting a password. This vulnerability could lead to security risks, as accounts without passwords may be susceptible to unauthorized access. Additionally, this issue violates best practices for secure user account management. The issue is fixed in version 2.19.0.

## References
- https://huntr.com/bounties/e79f7774-10fe-46b2-b522-e73b748e3b2d
- https://github.com/mlflow/mlflow/commit/149c9e18aa219bc47e86b432e130e467a36f4a17
- https://huntr.com/bounties/e79f7774-10fe-46b2-b522-e73b748e3b2d
- https://github.com/advisories/GHSA-4rj2-9gcx-5qhx
