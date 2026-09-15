# [H] Aegra has cross-user run injection in /threads/{thread_id}/runs (IDOR)

## Summary
Severity: High
Advisory: GHSA-m98r-6667-4wq7
CVE: CVE-2026-44504
CWE: CWE-285, CWE-639
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-m98r-6667-4wq7
Type: github-advisory

## Affected
- PyPI: `aegra-api` — affected >=0.9.0 <0.9.7

## Details
## Impact

Aegra deployments running 0.9.0 through 0.9.6 with multiple authenticated users on a shared instance are vulnerable to a cross-tenant IDOR. Any authenticated user (User A), given another user's `thread_id` (User B), can:

- Execute graph runs against User B's thread via `POST /threads/{thread_id}/runs`, `POST /threads/{thread_id}/runs/stream`, or `POST /threads/{thread_id}/runs/wait`
- Read User B's full checkpoint state via the resulting run's `output` field
- Inject arbitrary messages into User B's conversation history (persisted in B's checkpoint)
- Hide their activity from User B's `GET /threads/{thread_id}/runs` listing because the run carries A's `user_id`

The streaming variant is worse — the first SSE `event: values` frame returns the entire prior `messages` array immediately on connection, no graph execution needed.

Thread IDs are UUIDs but leak through frontend URLs, server logs, observability traces, and shared links. Guessing is not required.

## Patches

Fixed in **0.9.7**. The three affected endpoints now perform an SQL-level `user_id == authenticated_user.identity` check before calling `_prepare_run`. When the thread exists but is owned by another user, the response is `404 Thread not found` (matching the read-side pattern) to avoid leaking thread existence.

## Workarounds

If upgrade is not immediately possible, register an `@auth.on("threads", "create_run")` handler that explicitly verifies thread ownership against the authenticated identity before allowing the operation. Without a handler, no built-in authorization runs on these write paths.

Example mitigation handler:

```python
from langgraph_sdk import Auth

auth = Auth()

@auth.on("threads", "create_run")
async def enforce_thread_owner(ctx: Auth.types.AuthContext, value: dict):
    # Look up the thread, raise 404 if not owned by ctx.user.identity.
    # Implementation depends on your data layer.
    ...
```

## Root cause

Aegra's authorization model delegates per-resource policy to user-defined `@auth.on` handlers. When no handler is registered, `handle_event(...)` returns `None` and the request proceeds (default-allow). Read endpoints in `api/threads.py` add a defense-in-depth `user_id` filter at the SQL layer, but the run-creation endpoints in `api/runs.py` skipped that filter. Result: out-of-the-box deployments without custom auth handlers were vulnerable.

## Affected endpoints

- `POST /threads/{thread_id}/runs`
- `POST /threads/{thread_id}/runs/stream`
- `POST /threads/{thread_id}/runs/wait`

Stateless variants (`POST /runs`, `POST /runs/wait`, `POST /runs/stream`) are NOT affected — they generate a fresh `thread_id` server-side and never accept a caller-supplied one.

## Credits

- @JoJoTheBizarre — discovered and reported the vulnerability with a precise reproducer (#336)
- @victorjmarin and @jawhardjebbi — wrote the fix and added test coverage at unit, integration, and manual-auth e2e levels (#337)

## Resources

- Issue: https://github.com/aegra/aegra/issues/336
- Fix PR: https://github.com/aegra/aegra/pull/337
- Release: https://github.com/aegra/aegra/releases/tag/v0.9.7

## References
- https://github.com/aegra/aegra/security/advisories/GHSA-m98r-6667-4wq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44504
- https://github.com/aegra/aegra/issues/336
- https://github.com/aegra/aegra/pull/337
- https://github.com/aegra/aegra/commit/e1b2042254fd49072ca281bc35b3f2a3bed74b31
- https://github.com/aegra/aegra
- https://github.com/aegra/aegra/releases/tag/v0.9.7
