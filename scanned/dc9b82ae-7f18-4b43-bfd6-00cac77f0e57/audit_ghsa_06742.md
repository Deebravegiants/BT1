# [M] Suspended Coder users retain access to AI Bridge LLM proxy endpoints

## Summary
Severity: Medium
Advisory: GHSA-wqxv-w64v-5wh6
CVE: CVE-2026-55435
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-wqxv-w64v-5wh6
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7

## Details
### Summary

AI Bridge proxy endpoints authenticate via `Server.IsAuthorized` in `coderd/aibridgedserver`, which validates key format, expiry, secret and deleted or system users but does not check whether the account is suspended. Because suspension does not revoke existing API keys, a suspended user's unexpired token keeps working.

> **Note:** Practical impact is limited to already-issued API keys of suspended users until those keys are deleted.

### Impact

A suspended user with a previously issued long-lived token could continue calling AI Bridge LLM proxy endpoints, consuming paid provider resources billed to the deployment and, if injected MCP tools are enabled, invoking those tools. Access persists until the token expires, which may be months after suspension.

### Patches

The fix makes AI Bridge authorization reject non-active users like the standard API key middleware. AI Bridge was introduced in v2.30.0. The v2.29 ESR line is not affected.

The fix is available in the following releases:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |

### Workarounds

On suspension, delete the user's API keys via `DELETE /api/v2/users/{user}/keys`.

### Resources

- Fix: #26173

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22446) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-wqxv-w64v-5wh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-55435
- https://github.com/coder/coder/pull/26164
- https://github.com/coder/coder/pull/26173
- https://github.com/coder/coder/commit/0d2c9f904a8b75b888140fcc8fbf4633660cc787
- https://github.com/coder/coder
- https://github.com/coder/coder/releases/tag/v2.32.7
- https://github.com/coder/coder/releases/tag/v2.33.8
- https://github.com/coder/coder/releases/tag/v2.34.2
