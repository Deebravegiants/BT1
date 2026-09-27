# [M] BuildKit: Custom frontend could bypass Seccomp/AppArmor

## Summary
Severity: Medium
Advisory: GHSA-7236-3392-c5c6
CVE: CVE-2026-61711
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-7236-3392-c5c6
Type: github-advisory

## Affected
- Go: `github.com/moby/buildkit` — affected >=0 <0.31.1

## Details
### Impact
A custom frontend could send a crafted build request that disabled Seccomp and AppArmor protections for the build container, even if the user did not explicitly allow the `security.insecure` entitlement. Other security measures, like Linux capabilities were still applied to these containers.

### Patches
Problem has been fixed in versions v0.31.1+

### Workarounds
Only use BuildKit frontends from trusted providers.

## References
- https://github.com/moby/buildkit/security/advisories/GHSA-7236-3392-c5c6
- https://github.com/moby/buildkit
