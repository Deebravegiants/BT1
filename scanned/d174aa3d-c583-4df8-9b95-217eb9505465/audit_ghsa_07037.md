# [M] Coder's unbounded memory allocation in provisioner file upload allows authenticated denial of service

## Summary
Severity: Medium
Advisory: GHSA-f962-qm93-mj4c
CVE: CVE-2026-55079
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-f962-qm93-mj4c
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=2.24.0 <2.29.17

## Details
### Summary

`NewDataBuilder` in `provisionersdk/proto/dataupload.go` allocated a byte slice using the client-supplied `FileSize` from a `DataUpload` message without an upper-bound check. Although the DRPC wire limit is 4 MiB, the `FileSize` value itself was unconstrained

### Impact

An authenticated user able to reach the provisioner daemon serve endpoint could send a roughly 50-byte message declaring a huge `FileSize` (for example 1 TiB), triggering an unrecoverable Go out-of-memory abort that terminates `coderd`. This is a single-message denial of service affecting the entire deployment.

### Patches

The fix validates `FileSize` against an upper bound (`MaxFileSize = 100 MiB`) before allocation.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

Restrict access to the provisioner daemon serve endpoint to trusted provisioner daemon service accounts.

### Resources

- Fix: #25710

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22442) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-f962-qm93-mj4c
- https://github.com/coder/coder/pull/25710
- https://github.com/coder/coder
