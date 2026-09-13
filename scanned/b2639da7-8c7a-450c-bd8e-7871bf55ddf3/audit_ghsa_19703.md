# [C] Aim  path traversal in LockManager.release_locks

## Summary
Severity: Critical
Advisory: GHSA-4qcx-jx49-6qrh
CVE: CVE-2024-8769
CWE: CWE-22, CWE-29
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-4qcx-jx49-6qrh
Type: github-advisory

## Affected
- PyPI: `aim` — affected >=3.15.0

## Details
A vulnerability in the `LockManager.release_locks` function in aimhubio/aim (commit bb76afe) allows for arbitrary file deletion through relative path traversal. The `run_hash` parameter, which is user-controllable, is concatenated without normalization as part of a path used to specify file deletion. This vulnerability is exposed through the `Repo._close_run()` method, which is accessible via the tracking server instruction API. As a result, an attacker can exploit this to delete any arbitrary file on the machine running the tracking server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8769
- https://github.com/aimhubio/aim
- https://github.com/aimhubio/aim/blob/bb76afe6e9a54364f322520cc4fea2679238f904/aim/sdk/lock_manager.py#L140
- https://huntr.com/bounties/59d3472f-f581-4beb-a090-afd36a00ecf7
