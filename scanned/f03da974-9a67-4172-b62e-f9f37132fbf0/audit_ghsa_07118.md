# [H] Coder's workspace app upsert allows cross-workspace agent rebinding via user-controlled app ID

## Summary
Severity: High
Advisory: GHSA-9rjw-3gwp-f59v
CVE: CVE-2026-55429
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-9rjw-3gwp-f59v
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

`UpsertWorkspaceApp` overwrites an existing app's `agent_id` on a primary-key conflict and `insertAgentApp` accepts the app ID from the provisioner's `CompleteJob` payload without verifying it belongs to the workspace being built. `CompleteJob` runs under `dbauthz.AsProvisionerd` so the authorization layer does not block the cross-workspace upsert.

> **Note:** Exploitation requires elevated access as a template author or external provisioner operator.

### Impact

A user with template authorship or external provisioner access can submit a `CompleteJob` payload with a known victim app UUID and an attacker-controlled agent ID. On completion of the attacker's build the victim's app row is rebound to the attacker's agent so later app traffic such as IDE and terminal sessions is proxied to the attacker's workspace. App UUIDs are discoverable through the public API.

### Patches

The fix verifies that any existing `workspace_apps` row matching the supplied ID belongs to the workspace being built and rejects cross-workspace agent reassignment.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

None. Upgrading is required.

### Resources

- Fix: #26103

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22441) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-9rjw-3gwp-f59v
- https://github.com/coder/coder/pull/26103
- https://github.com/coder/coder
