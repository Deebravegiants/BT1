# [H] Woodpecker gRPC agent_id metadata can be spoofed- cross-tenant agent impersonation

## Summary
Severity: High
Advisory: GHSA-g7mm-9vx7-jm7h
CVE: CVE-2026-50141
CWE: CWE-290, CWE-639
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-g7mm-9vx7-jm7h
Type: github-advisory

## Affected
- Go: `go.woodpecker-ci.org/woodpecker/v3` — affected >=3.0.0 <3.14.1

## Details
### Impact
A vulnerability in Woodpecker CI's gRPC layer allowed any authenticated agent to impersonate any other agent on the same server by injecting a forged `agent_id` value into outgoing gRPC metadata. The server correctly verified the JWT token but then discarded the verified agent identity in favor of the client-supplied value.

### Patches
Direct patch: https://github.com/woodpecker-ci/woodpecker/pull/6567
Later proper fix: https://github.com/woodpecker-ci/woodpecker/pull/6569

### Workarounds
Disable org agents (`WOODPECKER_DISABLE_USER_AGENT_REGISTRATION=true`) and delete existing ones

### Resources
Public ref: https://github.com/woodpecker-ci/woodpecker/issues/6541
Private com: https://github.com/woodpecker-ci/woodpecker-security/issues/21

## References
- https://github.com/woodpecker-ci/woodpecker/security/advisories/GHSA-g7mm-9vx7-jm7h
- https://nvd.nist.gov/vuln/detail/CVE-2026-50141
- https://github.com/woodpecker-ci/woodpecker-security/issues/21
- https://github.com/woodpecker-ci/woodpecker/issues/6541
- https://github.com/woodpecker-ci/woodpecker/pull/6567
- https://github.com/woodpecker-ci/woodpecker/pull/6569
- https://github.com/woodpecker-ci/woodpecker
