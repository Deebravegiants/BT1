# [M] OpenClaw: Workspace dotenv files cannot override connector endpoint hosts

## Summary
Severity: Medium
Advisory: GHSA-55cf-xx38-4p9p
CVE: CVE-2026-45003
CWE: CWE-427, CWE-610
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-55cf-xx38-4p9p
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.22

## Details
## Summary
Workspace dotenv files cannot override connector endpoint hosts.

## Affected Packages / Versions
- Package: openclaw (npm)
- Affected versions: <= 2026.4.21
- Fixed version: 2026.4.22

## Impact
A workspace .env file could set connector endpoint variables for Matrix, Mattermost, IRC, or Synology-related connectors and redirect runtime traffic away from the operator-configured endpoint.

## Fix
Workspace .env loading now blocks those endpoint variables, including per-account Matrix homeserver suffixes and generic base-url/API-host style overrides. Trusted global runtime dotenv loading remains separate.

## Fix Commit(s)
- 0623079e98abf7202591f1b04a89755eb7ec9272

## Verification
- The fix commit is contained in the public v2026.4.22 tag.
- openclaw@2026.4.22 is published on npm and the compiled package contains the fix.
- Focused regression coverage for this path passed before publication.

OpenClaw thanks @qi-scape for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-55cf-xx38-4p9p
- https://nvd.nist.gov/vuln/detail/CVE-2026-45003
- https://github.com/openclaw/openclaw/commit/0623079e98abf7202591f1b04a89755eb7ec9272
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-connector-endpoint-host-override-via-workspace-dotenv-files
