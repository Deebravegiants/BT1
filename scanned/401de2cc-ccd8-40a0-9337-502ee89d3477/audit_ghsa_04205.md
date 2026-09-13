# [M] OpenClaw: Exported session HTML could keep unsafe markdown links

## Summary
Severity: Medium
Advisory: GHSA-w9hf-3pp7-pvxv
CVE: CVE-2026-53841
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-w9hf-3pp7-pvxv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.12

## Details
### Summary

Exported session HTML could keep unsafe markdown links. In affected versions, content rendered into an exported session could preserve unsafe `javascript:` or `data:` links in generated HTML.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run browser-side script if a trusted operator opens the exported file and activates the link. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.12`.

### Mitigations

do not open exported session HTML from untrusted content in a privileged browser profile until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w9hf-3pp7-pvxv
- https://nvd.nist.gov/vuln/detail/CVE-2026-53841
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-cross-site-scripting-via-unsafe-markdown-links-in-exported-session-html
