# [H] Langflow: Authenticated Users Can Read, Modify, and Delete Any Flow via Missing Ownership Check

## Summary
Severity: High
Advisory: GHSA-8c4j-f57c-35cf
CVE: CVE-2026-34046
CWE: CWE-639, CWE-862
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-8c4j-f57c-35cf
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.5.1
- PyPI: `langflow-base` — affected >=0 <0.5.1

## Details
## Vulnerability

### IDOR in `GET/PATCH/DELETE /api/v1/flow/{flow_id}`

The `_read_flow` helper in `src/backend/base/langflow/api/v1/flows.py` branched on the `AUTO_LOGIN` setting to decide whether to filter by `user_id`. When `AUTO_LOGIN` was `False` (i.e., authentication was enabled), neither branch enforced an ownership check — the query returned any flow matching the given UUID regardless of who owned it.

This exposed any authenticated user to:

- **Read** any other user's flow, including embedded plaintext API keys
- **Modify** the logic of another user's AI agents
- **Delete** flows belonging to other users

The vulnerability was introduced by the conditional logic that was meant to accommodate public/example flows (those with `user_id = NULL`) under auto-login mode, but inadvertently left the authenticated path without an ownership filter.

---

## Fix (PR #8956)

The fix removes the `AUTO_LOGIN` conditional entirely and unconditionally scopes the query to the requesting user:

```diff
-    auth_settings = settings_service.auth_settings
-    stmt = select(Flow).where(Flow.id == flow_id)
-    if auth_settings.AUTO_LOGIN:
-        stmt = stmt.where(
-            (Flow.user_id == user_id) | (Flow.user_id == None)  # noqa: E711
-        )
+    stmt = select(Flow).where(Flow.id == flow_id).where(Flow.user_id == user_id)
```

All three operations — read, update, and delete — route through `_read_flow`, so the single change covers the full attack surface. A cross-user isolation test (`test_read_flows_user_isolation`) was added to prevent regression.

---

## Acknowledgements

Langflow thanks the security researcher who responsibly disclosed this vulnerability:

- **[@chximn-dt](https://github.com/chximn-dt)**

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-8c4j-f57c-35cf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34046
- https://github.com/langflow-ai/langflow/pull/8956
- https://github.com/langflow-ai/langflow
