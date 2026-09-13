# [H] OpenClaw's POSIX node system.run safe-bin allowlist could be widened by shell expansion

## Summary
Severity: High
Advisory: GHSA-mhq8-78pj-5j79
CVE: CVE-2026-53831
CWE: CWE-200, CWE-284, CWE-367, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-mhq8-78pj-5j79
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.18

## Details
### Summary

On POSIX nodes, OpenClaw's `system.run` safe-bin checks could approve a command before shell expansion changed how the command was interpreted. A value that appeared to be a safe-bin argument could expand into additional shell words and become a file operand.

This issue is limited to paired POSIX node execution through `system.run` with safe-bin or allowlist-style auto-approval. It is not an unauthenticated node takeover.

### Affected configurations

This affects deployments where:

- a POSIX node is paired to the gateway
- `system.run` is reachable by an authenticated operator or agent flow
- exec policy uses safe-bin or allowlist-based auto-approval
- the approved command contains shell-expanded values that can change argv shape

### Impact

A lower-privilege operator flow could cause an approved safe-bin command to read a node-local file that was not intended by the policy. Depending on the local files available to the node process, this could expose OpenClaw configuration data or other node-local information.

The issue is a policy-enforcement gap in argv validation, not a general statement that every safe-bin command is unsafe.

### Patched Versions

The first stable patched version is `2026.5.18`.

### Mitigations

Upgrade to `openclaw@2026.5.18` or later. Before upgrading, avoid broad safe-bin auto-approval for commands that can read arbitrary paths, and prefer explicit approval for node commands that touch local files.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mhq8-78pj-5j79
- https://nvd.nist.gov/vuln/detail/CVE-2026-53831
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-file-read-via-shell-expansion-in-system-run-safe-bin-allowlist
