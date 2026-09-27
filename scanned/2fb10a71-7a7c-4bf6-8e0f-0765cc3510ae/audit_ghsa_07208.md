# [M] OpenClaw: Node pairing reconnection could confuse approval scope state

## Summary
Severity: Medium
Advisory: GHSA-83w9-h5wv-j9xm
CVE: CVE-2026-53838
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-83w9-h5wv-j9xm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.27

## Details
### Summary

Node pairing reconnection could confuse approval scope state. In affected versions, a paired or reconnecting node session could mutate pairing state in a way that changed the approval scope decision.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could restore or present broader node authority than the operator intended. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.27`.

### Mitigations

revoke unexpected node pairings and re-pair only trusted nodes until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-83w9-h5wv-j9xm
- https://nvd.nist.gov/vuln/detail/CVE-2026-53838
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-node-pairing-state-mutation-via-reconnection
