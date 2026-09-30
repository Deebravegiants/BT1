# [H] Go package github.com/edgelesssys/marblerun CLI commands susceptible to MITM attacks

## Summary
Severity: High
Advisory: GHSA-j3rq-4xjw-xg63
CWE: CWE-300
Ecosystem: Go
Published: 2023-12-04
Source: https://github.com/advisories/GHSA-j3rq-4xjw-xg63
Type: github-advisory

## Affected
- Go: `github.com/edgelesssys/marblerun` — affected >=0 <1.4.0

## Details
### Impact
Any CLI command issued to a Coordinator after the Manifest has been set, is susceptible to be redirected to another MarbleRun Coordinator instance, which runs the same binary, but potentially a different manifest.

### Patches
 The issue has been patched in [`v1.4.0`](https://github.com/edgelesssys/marblerun/releases/tag/v1.4.0)

### Workarounds

Directly using the REST API of the Coordinator and manually verifying and pinning the certificate to a set Manifest avoids the issue.

## References
- https://github.com/edgelesssys/marblerun/security/advisories/GHSA-j3rq-4xjw-xg63
- https://github.com/edgelesssys/marblerun
- https://github.com/edgelesssys/marblerun/releases/tag/v1.4.0
