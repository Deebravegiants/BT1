# [M] OpenClaw's config env vars allowed startup env injection into service runtime

## Summary
Severity: Medium
Advisory: GHSA-8fmp-37rc-p5g7
CVE: CVE-2026-22177
CWE: CWE-15
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-8fmp-37rc-p5g7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
### Summary
OpenClaw allowed dangerous process-control environment variables from `env.vars` (for example `NODE_OPTIONS`, `LD_*`, `DYLD_*`) to flow into gateway service runtime environments, enabling startup-time code execution in the OpenClaw process context.

### Details
`collectConfigEnvVars()` accepted unfiltered keys from config and those values were merged into the daemon install environment in `buildGatewayInstallPlan()`. Before the fix, startup-control variables were not blocked in this path.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published affected version: `2026.2.19-2` (published February 19, 2026)
- Affected range (structured): `<=2026.2.19-2 || =2026.2.19`
- Patched version (pre-set for next release): `>= 2026.2.21`

### Fix Commit(s)
- `2cdbadee1f8fcaa93302d7debbfc529e19868ea4`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.21`). Once that npm release is published, this advisory is ready to publish without further content edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8fmp-37rc-p5g7
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w9j9-w4cp-6wgr
- https://nvd.nist.gov/vuln/detail/CVE-2026-22177
- https://github.com/openclaw/openclaw/commit/2cdbadee1f8fcaa93302d7debbfc529e19868ea4
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-environment-variable-injection-via-config-env-vars
