# [M] OpenClaw browser navigation guard allowed non-network URL schemes, enabling authenticated browser-tool users to access file:// local files

## Summary
Severity: Medium
Advisory: GHSA-45cg-2683-gfmq
CVE: CVE-2026-32008
CWE: CWE-610
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-45cg-2683-gfmq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
## Impact

`assertBrowserNavigationAllowed()` validated only `http:`/`https:` network targets but implicitly allowed other schemes. An authenticated gateway user could navigate browser sessions to `file://` URLs and read local files via browser snapshot/extraction flows.

## Affected Component

- `src/browser/navigation-guard.ts`

## Technical Reproduction

1. Authenticate to a gateway that has browser tooling enabled.
2. Invoke browser navigation with a `file://` URL (for example `file:///etc/passwd`).
3. Read page content through browser snapshot/extract actions.

## Demonstrated Impact

An attacker with valid gateway credentials and browser-tool access can exfiltrate local files readable by the OpenClaw process user (for example config/secrets in that user context).

## Environment

- OpenClaw browser tool enabled
- Attacker has authenticated access capable of invoking browser actions

## Remediation Advice

Reject unsupported navigation schemes and allow only explicitly safe non-network URLs. OpenClaw now blocks non-network schemes (such as `file:`, `data:`, and `javascript:`) while preserving `about:blank`.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.19-2`
- Patched in planned next release: `2026.2.21`

## Fix Commit(s)

- `220bd95eff6838234e8b4b711f86d4565e16e401`

## Release Process Note

`patched_versions` is pre-set to the planned next release (`2026.2.21`) so once npm `2026.2.21` is published, the advisory can be published directly.

OpenClaw thanks @q1uf3ng for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-45cg-2683-gfmq
- https://github.com/openclaw/openclaw/commit/220bd95eff6838234e8b4b711f86d4565e16e401
- https://github.com/openclaw/openclaw
