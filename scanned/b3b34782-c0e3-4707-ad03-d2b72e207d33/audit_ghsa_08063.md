# [M] RediSearch Query Injection in @langchain/langgraph-checkpoint-redis

## Summary
Severity: Medium
Advisory: GHSA-5mx2-w598-339m
CVE: CVE-2026-27022
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-5mx2-w598-339m
Type: github-advisory

## Affected
- npm: `@langchain/langgraph-checkpoint-redis` — affected >=0 <1.0.2

## Details
## Summary

A query injection vulnerability exists in the `@langchain/langgraph-checkpoint-redis` package's filter handling. The `RedisSaver` and `ShallowRedisSaver` classes construct RediSearch queries by directly interpolating user-provided filter keys and values without proper escaping. RediSearch has special syntax characters that can modify query behavior, and when user-controlled data contains these characters, the query logic can be manipulated to bypass intended access controls.

## Attack surface

The core vulnerability was in the `list()` methods of both `RedisSaver` and `ShallowRedisSaver`: these methods failed to escape RediSearch special characters in filter keys and values when constructing queries. When unescaped data containing RediSearch syntax was used, the injected operators were interpreted by RediSearch rather than treated as literal search values.

This escaping bug enabled the following attack vector:

- **Thread boundary escape via OR operator**: RediSearch uses `|` as an OR operator with specific precedence rules. A query like `A B | C` is interpreted as `(A AND B) OR C`. By injecting `}) | (@thread_id:{*` into a filter value, an attacker can append an OR clause that matches all threads, effectively bypassing the thread isolation constraint.

The injected query `(@thread_id:{legitimate-thread}) (@source:{x}) | (@thread_id:{*})` matches:

- Documents with `thread_id:legitimate-thread AND source:x`, OR
- Documents with ANY `thread_id`

The second clause matches all threads, bypassing thread isolation entirely.

## Who is affected?

Applications are vulnerable if they:

- **Pass user-controlled input to filter parameters** — When using `getStateHistory()` or `checkpointer.list()` with filter values derived from user input, HTTP parameters, or other untrusted sources.
- **Use Redis checkpointing in multi-tenant applications** — Applications that rely on thread isolation to separate data between users or tenants are at risk of cross-tenant data access.

The most common attack vector is through API endpoints that expose filtering capabilities to end users, allowing them to search or filter their conversation history.

## Impact

Attackers who control filter input can bypass thread isolation by injecting RediSearch OR operators to construct queries that match all threads regardless of the intended thread constraint. This enables access to checkpoint data from threads the attacker is not authorized to view.

Key severity factors:

- Enables complete bypass of thread-based access controls
- Sensitive conversation data from other users may be exposed
- Affects multi-tenant applications relying on thread isolation for data separation
- Requires only control over filter input values (common in user-facing APIs)

## Exploit example

```typescript
import { RedisSaver } from "@langchain/langgraph-checkpoint-redis";

const saver = new RedisSaver({ /* redis config */ });

// Normal usage - should only see thread "user-123-thread"
const legitHistory = saver.list({
  configurable: { thread_id: "user-123-thread" }
}, {
  filter: { source: "loop" }
});

// Attacker crafts malicious filter value
const attackerFilter = {
  source: "x}) | (@thread_id:{*"  // Injects OR clause matching ALL threads
};

// This produces a query like:
// (@thread_id:{user-123-thread}) (@source:{x}) | (@thread_id:{*})
// Due to precedence, this matches ALL threads!

const stolenHistory = saver.list({
  configurable: { thread_id: "user-123-thread" }
}, {
  filter: attackerFilter
});

// stolenHistory now contains checkpoints from ALL threads - DATA LEAKED!
```

## Security hardening changes

The 1.0.2 patch introduces the following changes:

- **Escape utility function**: A new `escapeRediSearchTagValue()` function properly escapes all RediSearch special characters (`- . < > { } [ ] " ' : ; ! @ # $ % ^ & * ( ) + = ~ | \ ? /`) by prefixing them with backslashes.
- **Filter key escaping**: All filter keys are escaped before being used in query construction.
- **Filter value escaping**: All filter values are escaped before being interpolated into RediSearch tag queries.

## Migration guide

### No changes needed for most users

The fix is backward compatible. Existing code will work without modifications—filter values that previously worked will continue to work, with the added protection against injection:

```typescript
import { RedisSaver } from "@langchain/langgraph-checkpoint-redis";

// Works exactly as before, now with injection protection
const history = saver.list(config, {
  filter: { source: "loop" }
});
```

### If you were relying on special characters

If your application intentionally used RediSearch syntax in filter values (unlikely but possible), be aware that these characters will now be escaped and treated as literals.

### For applications with user-facing filters

No code changes required, but this is a good time to review your API design:

```typescript
// Before: Vulnerable to injection
app.get("/history", async (req, res) => {
  const history = await saver.list(config, {
    filter: req.query.filter  // User-controlled - was vulnerable
  });
});

// After: Now safe, but consider validating allowed filter keys
app.get("/history", async (req, res) => {
  const allowedKeys = ["source", "step"];
  const sanitizedFilter = Object.fromEntries(
    Object.entries(req.query.filter || {})
      .filter(([key]) => allowedKeys.includes(key))
  );
  const history = await saver.list(config, {
    filter: sanitizedFilter
  });
});
```

> **Recommendation**: Even with the fix in place, consider validating that filter keys are from an allowed list as a defense-in-depth measure.

## References

- [RediSearch Query Syntax](https://redis.io/docs/interact/search-and-query/query/)
- [LangGraph Checkpoint Documentation](https://langchain-ai.github.io/langgraphjs/)

## References
- https://github.com/langchain-ai/langgraphjs/security/advisories/GHSA-5mx2-w598-339m
- https://nvd.nist.gov/vuln/detail/CVE-2026-27022
- https://github.com/langchain-ai/langgraphjs/pull/1943
- https://github.com/langchain-ai/langgraphjs/commit/814c76dc3938d0f6f7e17ca3bc11d6a12270b2a1
- https://github.com/langchain-ai/langgraphjs
- https://github.com/langchain-ai/langgraphjs/releases/tag/@langchain/langgraph-checkpoint-redis@1.0.2
