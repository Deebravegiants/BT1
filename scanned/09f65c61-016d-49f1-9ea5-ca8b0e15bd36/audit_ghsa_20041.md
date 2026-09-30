# [H] Yapscan's report receiver server vulnerable to path traversal and log injection

## Summary
Severity: High
Advisory: GHSA-9h6h-9g78-86f7
CWE: CWE-117, CWE-22, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-12-29
Source: https://github.com/advisories/GHSA-9h6h-9g78-86f7
Type: github-advisory

## Affected
- Go: `github.com/fkie-cad/yapscan` — affected >=0.18.0 <0.19.1

## Details
### Impact

If you make use of the **report receiver server** (experimental), a client may be able to forge requests such that arbitrary files on the host can be overwritten (subject to permissions of the yapscan server), leading to loss of data. This is particularly problematic if you do not authenticate clients and/or run the server with elevated permissions.

### Patches

Vulnerable versions:

- v0.18.0
- v0.19.0 (unreleased)

This problem is patched in version v0.19.1

### Workarounds

Update to the newer version is highly encouraged!

Measures to reduce the risk of this include authenticating clients (see `--client-ca` flag) and containerization of the yapscan server.

### References

The tracking issue is #35. There you can find the commits, fixing the issue.

## References
- https://github.com/fkie-cad/yapscan/security/advisories/GHSA-9h6h-9g78-86f7
- https://github.com/fkie-cad/yapscan/issues/35
- https://github.com/fkie-cad/yapscan/commit/a75a20b50be673b96b1d42187b97f8cfe60728df
- https://github.com/fkie-cad/yapscan/commit/fef9a33ceb66f6b929839f7eaf393b629681bc5d
- https://github.com/fkie-cad/yapscan
- https://github.com/fkie-cad/yapscan/releases/tag/v0.19.1
