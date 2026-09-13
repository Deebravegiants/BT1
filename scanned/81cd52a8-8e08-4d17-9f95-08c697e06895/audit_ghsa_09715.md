# [M] OpenClaw: OpenShell `mirror` mode can convert untrusted sandbox files into explicitly enabled workspace hooks and execute them on the host during gateway startup

## Summary
Severity: Medium
Advisory: GHSA-42mx-vp8m-j7qh
CVE: CVE-2026-41355
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-42mx-vp8m-j7qh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary
OpenShell `mirror` mode can convert untrusted sandbox files into explicitly enabled workspace hooks and execute them on the host during gateway startup

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: Real on shipped <=2026.3.22 OpenShell mirror sync, but exploit needs mirror mode plus hooks enabled plus explicit hook opt-in plus restart, so high is overstated even though the direct fix shipped in v2026.3.28.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.24`
- Patched versions: `>= 2026.3.28`
- First stable tag containing the fix: `v2026.3.28`

## Fix Commit(s)
- `c02ee8a3a4cb390b23afdf21317aa8b2096854d1` — 2026-03-25T19:59:07Z

## Release Process Note
- The fix is already present in released version `2026.3.28`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-42mx-vp8m-j7qh
- https://nvd.nist.gov/vuln/detail/CVE-2026-41355
- https://github.com/openclaw/openclaw/commit/c02ee8a3a4cb390b23afdf21317aa8b2096854d1
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openshell-arbitrary-code-execution-via-mirror-mode-sandbox-file-conversion
