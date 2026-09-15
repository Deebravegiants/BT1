# [M] Coder: Devcontainer recreate endpoint missing write authorization allows read-only roles to destroy containers

## Summary
Severity: Medium
Advisory: GHSA-jqj2-x4c5-jfxm
CVE: CVE-2026-55433
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-jqj2-x4c5-jfxm
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

The devcontainer recreate endpoint relied on route middleware that checked only `ActionRead` on the workspace and, unlike the sibling delete endpoint, performed no `ActionUpdate` check before triggering the destructive rebuild.

> **Note:** Exploitation requires an existing low-privilege role with access to the target workspace.

### Impact

Any authenticated principal with read-only workspace access, such as a Template Admin or Org Template Admin, could recreate a devcontainer, destroying uncommitted in-container state and, if called repeatedly, denying service. This is an authorization bypass leading to data loss and denial of service.

### Patches

The fix adds an explicit `ActionUpdate` authorization check before the agent is dialed like the delete endpoint.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

None.

### Resources

- Fix: #25812

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22454) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-jqj2-x4c5-jfxm
- https://github.com/coder/coder/pull/25812
- https://github.com/coder/coder
