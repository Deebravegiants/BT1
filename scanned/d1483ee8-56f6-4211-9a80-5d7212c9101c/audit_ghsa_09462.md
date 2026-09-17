# [M] Crabbox contains a path traversal vulnerability in the Islo provider's workspace path resolution

## Summary
Severity: Medium
Advisory: GHSA-3cjv-h753-qf7h
CVE: CVE-2026-45224
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-3cjv-h753-qf7h
Type: github-advisory

## Affected
- Go: `github.com/openclaw/crabbox` — affected >=0 <0.9.0

## Details
Crabbox before 0.9.0 contains a path traversal vulnerability in the Islo provider's workspace path resolution that allows attackers to supply absolute or relative paths that resolve outside the intended /workspace directory. Attackers can craft a malicious .crabbox.yaml or crabbox.yaml file with traversal sequences to cause arbitrary file deletion and overwrite when sync.delete is enabled, as the workspace preparation logic executes rm -rf and mkdir -p operations on the resolved path without proper validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45224
- https://github.com/openclaw/crabbox/pull/65
- https://github.com/openclaw/crabbox/commit/6b07193fb5670aac315ea47215651c67b8127868
- https://github.com/openclaw/crabbox
- https://github.com/openclaw/crabbox/releases/tag/v0.9.0
- https://www.vulncheck.com/advisories/crabbox-path-traversal-via-islo-provider-workspace-resolution
