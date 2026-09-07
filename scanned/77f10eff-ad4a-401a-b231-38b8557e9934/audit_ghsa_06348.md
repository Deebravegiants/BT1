# [M] Open WebUI: Unapproved accounts can open terminal sessions via a WebSocket auth path missing the role check

## Summary
Severity: Medium
Advisory: GHSA-5gpj-vj23-vhhv
CVE: CVE-2026-70490
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-5gpj-vj23-vhhv
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.8.8 <0.11.0

## Details
## Summary
The terminal WebSocket route authenticates its own first-message JWT instead of going through the HTTP dependency chain, and never applies the role check that `get_verified_user` enforces on every HTTP terminal route. An account whose role is `pending`, meaning registered but not approved, or approved and later deactivated back to `pending`, can therefore open an interactive terminal session that the HTTP terminal endpoints would refuse. The missing control is the verified-user role gate, not the terminal access grants, which are evaluated correctly.

## Preconditions
At least one terminal server must be configured, which is off by default, and its access grants must cover the account: either public read (`principal_id: "*"`) or a group the account still belongs to. The attacker needs a valid, unexpired JWT for a `pending` account and the terminal server id. Both are obtainable by an account that registered while approvals are pending, or by one that held access and was deactivated, since deactivation sets the role to `pending` without revoking the token, which lasts four weeks by default. Deployments with no terminal server configured, or whose terminal grants are admin-only, are not affected.

## Impact
A deployment loses the account-approval boundary for terminal access. An unapproved or deactivated account gets interactive shell access, file browsing and terminal-backed tooling in the terminal environment, for as long as its token remains valid. Because the HTTP terminal routes correctly reject the same account, the two planes disagree, so an administrator who deactivates a user sees access revoked over HTTP while the WebSocket keeps working. The terminal access grants themselves are not bypassed: an account with no grant is still refused, so this only widens access to terminals already shared broadly or with a group the account remains in.

## Fix
Fixed in v0.11.0 by https://github.com/open-webui/open-webui/pull/27537. Token decoding, revocation checking, user lookup and the role check are consolidated into a single `get_verified_user_by_token` helper, and both the terminal WebSocket route and the Socket.IO handshake now go through it. The role set lives in one constant shared with the HTTP gate so the two cannot drift apart again. Upgrading fully resolves the issue; no configuration change is required.

## Root cause
Affected component: `backend/open_webui/routers/terminals.py`, the `_resolve_authenticated_connection` helper backing the `/{server_id}/api/terminals/{session_id}` WebSocket route. Affected setup: every build from v0.8.8 onward, since the route was introduced there.

WebSocket handshakes cannot use FastAPI dependencies, so this route reimplemented authentication inline. The reimplementation reproduced the parts that are visible in the token, that it decodes and that the user row exists, and silently dropped the part that lives in the database row, the role check. Authorization then ran on two independent code paths with no shared definition of what an authenticated user is, and only one of them was updated when the role gate was introduced.

## Credits
Reported by @rexpository.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-5gpj-vj23-vhhv
- https://github.com/open-webui/open-webui
