# [M] OpenClaw: Mattermost callback dispatch allowed non-allowlisted sender actions

## Summary
Severity: Medium
Advisory: GHSA-8883-9w57-vwv6
CVE: CVE-2026-35652
CWE: CWE-285, CWE-696, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-8883-9w57-vwv6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Mattermost interactive callback dispatch could run action handlers before normal sender authorization checks completed.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `a47722de7e3c9cbda8d5512747ca7e3bb8f6ee66`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- extensions/mattermost/src/mattermost/interactions.ts now requires callback authorization before dispatching actions.
- extensions/mattermost/src/mattermost/monitor.ts routes callback authorization through the same sender and allowlist policy used for normal ingress.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8883-9w57-vwv6
- https://nvd.nist.gov/vuln/detail/CVE-2026-35652
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/a47722de7e3c9cbda8d5512747ca7e3bb8f6ee66
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unauthorized-action-execution-via-callback-dispatch
