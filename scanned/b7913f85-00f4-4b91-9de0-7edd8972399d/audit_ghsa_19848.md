# [M] Aim Relative Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p6x3-v6g3-7557
CVE: CVE-2024-6483
CWE: CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-p6x3-v6g3-7557
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=0

## Details
A vulnerability in the `runs/delete-batch` endpoint of aimhubio/aim version 3.19.3 allows for arbitrary file or directory deletion through path traversal. The endpoint does not mitigate path traversal when handling user-specified run-names, which are used to specify log/metadata files for deletion. This can be exploited to delete arbitrary files or directories, potentially causing denial of service or data loss.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6483
- https://github.com/aimhubio/aim
- https://huntr.com/bounties/dc45d480-e579-4af4-8603-c52ecfd5e363
