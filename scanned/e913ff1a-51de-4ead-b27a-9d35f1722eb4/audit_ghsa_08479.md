# [C] Crabbox: environment variable exposure vulnerability

## Summary
Severity: Critical
Advisory: GHSA-fm77-94qm-4894
CVE: CVE-2026-8634
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-fm77-94qm-4894
Type: github-advisory

## Affected
- Go: `github.com/openclaw/crabbox` — affected >=0 <0.12.0

## Details
Crabbox prior to v0.12.0 contains an environment variable exposure vulnerability that allows attackers with access to a malicious or compromised repository to forward local secrets such as API tokens, cloud credentials, and broker tokens into the remote command environment. Attackers can exploit overly permissive environment variable allowlisting in repo-local Crabbox configuration to serialize sensitive environment variables into remote command execution, exposing credentials to the remote environment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8634
- https://github.com/openclaw/crabbox/pull/78
- https://github.com/openclaw/crabbox/commit/eaae40ae4ce009e60633f16f7f19600c74557f6f
- https://github.com/advisories/GHSA-fm77-94qm-4894
- https://github.com/openclaw/crabbox
- https://github.com/openclaw/crabbox/releases/tag/v0.12.0
- https://www.vulncheck.com/advisories/crabbox-environment-variable-information-disclosure
