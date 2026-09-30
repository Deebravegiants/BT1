# [M] OpenClaw: BlueBubbles (optional plugin) pairing/allowlist mismatch when allowFrom is empty

## Summary
Severity: Medium
Advisory: GHSA-jwf4-8wf4-jf2m
CVE: CVE-2026-22170
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-jwf4-8wf4-jf2m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
BlueBubbles is an optional OpenClaw channel plugin. A configuration-sensitive access-control mismatch allowed DM senders to be treated as authorized when `dmPolicy` was `pairing` or `allowlist` and `allowFrom` was empty/unset.

### Severity Rationale (Medium)
Severity is set to **medium** because:
- this affects an optional plugin, not core messaging surfaces;
- many deployments use owner-controlled/private BlueBubbles identities with limited external reachability;
- practical exploitability depends on an untrusted sender being able to reach that specific BlueBubbles account identifier.

In typical personal/self-hosted BlueBubbles setups, the mapped Apple identity is single-owner and not broadly reachable, so this is usually low practical risk.

Risk is higher in deployments where the identifier is publicly reachable and/or agent tool permissions are broad.

### Technical Details
1. BlueBubbles DM policy defaults to `pairing` (`dmPolicy ?? "pairing"`).
2. Effective allowlist can be empty (`effectiveAllowFrom`).
3. DM/reaction authorization called `isAllowedBlueBubblesSender(...)`.
4. That delegated to shared `isAllowedParsedChatSender(...)`, which previously returned `true` for empty allowlists.
5. Result: unknown senders could bypass intended pairing/allowlist gating when `allowFrom` was empty.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Vulnerable versions: `<= 2026.2.21-2`
- Planned fixed version: `2026.2.22`

### Fix
The shared parsed-chat allowlist helper now fails closed on empty allowlists, restoring expected BlueBubbles DM gating behavior. BlueBubbles inbound gating was also refactored to use one shared DM/group decision helper for both message and reaction paths to reduce future drift.

### Fix Commit(s)
- `9632b9bcf032c5f2280c3103961fde912ab1f920`
- `2ba6de7eaad812e5e8603018e14e54e96bdd57dd`
- `51c0893673de8e5cea64e64351dbfa4680ba0dec`
- `4540790cb62412676f7b61cfc6e47443f84a251e`

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jwf4-8wf4-jf2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-22170
- https://github.com/openclaw/openclaw/commit/2ba6de7eaad812e5e8603018e14e54e96bdd57dd
- https://github.com/openclaw/openclaw/commit/4540790cb62412676f7b61cfc6e47443f84a251e
- https://github.com/openclaw/openclaw/commit/51c0893673de8e5cea64e64351dbfa4680ba0dec
- https://github.com/openclaw/openclaw/commit/9632b9bcf032c5f2280c3103961fde912ab1f920
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-bluebubbles-access-control-bypass-via-empty-allowfrom-configuration
