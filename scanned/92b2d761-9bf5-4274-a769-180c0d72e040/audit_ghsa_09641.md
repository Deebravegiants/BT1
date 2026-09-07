# [C] Daptin has Unauthenticated Path Traversal and Zip Slip

## Summary
Severity: Critical
Advisory: GHSA-9cp7-j3f8-p5jx
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-9cp7-j3f8-p5jx
Type: github-advisory

## Affected
- Go: `github.com/daptin/daptin` — affected >=0 <0.12.0

## Details
### Impact
The `cloudstore.file.upload` action in `server/actions/action_cloudstore_file_upload.go` writes user-supplied filenames directly to disk without proper validation. 

This allows unauthenticated attackers to perform path traversal and zip slip attacks, leading to arbitrary file write and potential remote code execution.

**CVSS Score:** 10.0 Critical
**CVSS Vector:** CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:H
**CWE:** CWE-22 (Path Traversal)

### Patches

Upgrade to a patched version once released. The vulnerability affects all versions <= v0.11.3 (latest).

### Workarounds

Restrict access to the cloudstore.file.upload action through authentication and authorization controls until a patch is available.

## References
- https://github.com/daptin/daptin/security/advisories/GHSA-9cp7-j3f8-p5jx
- https://github.com/daptin/daptin/commit/8d626bbb14f82160a08cbca53e0749f475f5742c
- https://github.com/daptin/daptin
