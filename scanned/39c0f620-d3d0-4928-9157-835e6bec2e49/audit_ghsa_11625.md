# [H] OpenClaw's `tools.exec.safeBins` PATH-hijack allowed trojan binaries to bypass allowlist checks

## Summary
Severity: High
Advisory: GHSA-g75x-8qqm-2vxp
CVE: CVE-2026-32015
CWE: CWE-426, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-g75x-8qqm-2vxp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.21 <2026.2.19

## Details
## Summary

`tools.exec.safeBins` allowlist checks could be bypassed by PATH-hijacked binaries, allowing execution of attacker-controlled trojan binaries under an allowlisted executable name.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Latest published version at triage time: `2026.2.17`
- Affected range: `>= 2026.1.21 < 2026.2.18`
- Patched version: `2026.2.19`

## Impact

In allowlist mode, `safeBins` validation previously accepted a resolved executable path based on executable name and argument shape, without enforcing trusted executable directories. If an attacker could influence process PATH resolution before gateway startup (or otherwise control the gateway launch environment), a trojan binary with an allowlisted name (for example `jq`) could be executed.

## Severity Rationale

This issue is rated `medium` because exploitation requires an additional precondition: influencing the gateway process PATH / launch environment. Request-scoped PATH injection is blocked for host execution.

## Fix

`safeBins` now requires the resolved executable path to come from trusted bin directories (system defaults plus gateway startup PATH), closing the bypass.

## Fix Commit(s)

- 28bac46c92069dc728524fbf383024c1b64e5c23

OpenClaw thanks @jackhax for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g75x-8qqm-2vxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-32015
- https://github.com/openclaw/openclaw/commit/28bac46c92069dc728524fbf383024c1b64e5c23
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-path-hijacking-bypass-in-tools-exec-safebins-allowlist-validation
