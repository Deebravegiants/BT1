# [H] OpenClaw's marketplace runtime extension metadata could point at unscanned payloads

## Summary
Severity: High
Advisory: GHSA-v6r2-jh58-xx6w
CVE: CVE-2026-53810
CWE: CWE-284, CWE-78, CWE-829, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-v6r2-jh58-xx6w
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.18

## Details
### Summary

Marketplace runtime extension metadata could point at unscanned payloads. In affected versions, a package selected for installation by a trusted operator could redirect runtime loading toward hidden package content that was not scanned as expected.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could load plugin code outside the reviewed package entry points. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.18`.

### Mitigations

Install only trusted plugins and keep plugin allowlists explicit until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v6r2-jh58-xx6w
- https://nvd.nist.gov/vuln/detail/CVE-2026-53810
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-code-execution-via-unscanned-marketplace-runtime-extension-metadata
