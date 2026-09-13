# [M] Coder: Zip upload decompression lacks aggregate size limit, enabling denial of service

## Summary
Severity: Medium
Advisory: GHSA-2mg2-p7r7-g27f
CVE: CVE-2026-55078
CWE: CWE-409, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-2mg2-p7r7-g27f
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=2.17.0 <2.29.17

## Details
### Summary

`POST /api/v2/files` converts zip uploads to tar in memory via `CreateTarFromZip`, which enforced a per-entry size limit but no aggregate limit on total decompressed output, writing to an unbounded in-memory buffer.

> **Note:** Exploitation requires authenticated file-upload access and the impact is limited to availability (denial of service).

### Impact

An authenticated user could upload a zip within the 100 MiB upload limit but containing many highly compressible entries whose decompressed size exhausted memory, crashing `coderd` before any RBAC check. Repeated requests could keep the service unavailable. This is a denial of service; it does not allow data disclosure or code execution.

### Patches

The fix adds a metadata preflight check that sums projected entry sizes and a streaming writer that enforces the aggregate limit during decompression.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

Restrict file-upload permissions to trusted users or place a reverse proxy with request-body size limits in front of `coderd`.

### Resources

- Fix: #25877

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22438) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-2mg2-p7r7-g27f
- https://github.com/coder/coder/pull/25877
- https://github.com/coder/coder
