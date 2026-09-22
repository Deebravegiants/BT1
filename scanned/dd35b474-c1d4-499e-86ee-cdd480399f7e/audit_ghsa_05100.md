# [M] LangGraph has NoSQL parameter injection in MongoDBSaver, allowing cross-tenant state access

## Summary
Severity: Medium
Advisory: GHSA-98xf-r82g-9mhx
CVE: CVE-2026-48121
CWE: CWE-943
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-98xf-r82g-9mhx
Type: github-advisory

## Affected
- npm: `@langchain/langgraph-checkpoint-mongodb` — affected >=0 <1.3.1

## Details
## Summary

A NoSQL injection vulnerability existed in `MongoDBSaver` where checkpoint identifier fields from `config.configurable` were used in MongoDB queries without strict type enforcement. In vulnerable versions, attacker-controlled object payloads (for example MongoDB operators like `$gt` and `$ne`) could be interpreted as query operators instead of literal identifier values.

This could bypass intended thread scoping and return checkpoints from other tenants.

## Attack surface

The vulnerable path was in `MongoDBSaver.getTuple()`, where `thread_id`, `checkpoint_ns`, and `checkpoint_id` were used in MongoDB `find()` queries. The same unvalidated values were then reused to fetch pending writes.

Applications were exposed when untrusted input was forwarded into `config.configurable` (for example, directly from request bodies or query parameters) without string coercion or schema validation.

## Who is affected?

Applications are vulnerable if they:

- Use `@langchain/langgraph-checkpoint-mongodb` with multi-tenant or user-isolated thread models.
- Accept user-controlled values for `thread_id`, `checkpoint_ns`, or `checkpoint_id`.
- Pass those values into `app.invoke()`, `app.stream()`, or direct saver methods without validation.

Applications are generally not vulnerable if they:

- Use server-issued identifiers only.
- Source `thread_id` from trusted URL params that remain strings.
- Enforce schema validation that rejects non-string identifier fields.

## Impact

An attacker with control over configurable checkpoint identifiers could read checkpoint data outside their authorized thread boundary.

Potentially exposed data includes:

- Checkpoint state
- Metadata
- Pending writes

This is a confidentiality issue with cross-tenant data disclosure risk.

## Exploit example

An attacker-controlled request can inject MongoDB operators:

```ts
graph = new StateGraph(...)
  .compile({
    checkpointer: new MongoDBSaver()
  });

graph.invoke(..., {
  configurable: {  
    "thread_id": { "$gt": "" },
    "checkpoint_ns": { "$ne": null }
  }
});
```

If this payload is forwarded into `config.configurable`, the resulting query may match checkpoints outside the intended tenant/thread scope.

## Security hardening changes

Version `1.3.1` hardens `@langchain/langgraph-checkpoint-mongodb` by adding runtime validation for configurable checkpoint identifiers and rejecting invalid values before MongoDB query/write paths execute.

The patch also includes regression tests covering object/operator payloads across affected methods.

## Migration guide

Upgrade to `@langchain/langgraph-checkpoint-mongodb@1.3.1` or later.

No API migration is required for valid callers. However, applications that currently pass non-string identifier values in `config.configurable` will now receive explicit errors and should normalize/validate inputs.

As defense in depth, validate identifier fields at API boundaries and avoid passing raw client objects into graph config.

## Resources

- Issue: https://github.com/langchain-ai/langgraphjs/issues/2351
- Fix PR: https://github.com/langchain-ai/langgraphjs/pull/2397

## References
- https://github.com/langchain-ai/langgraphjs/security/advisories/GHSA-98xf-r82g-9mhx
- https://github.com/langchain-ai/langgraphjs/issues/2351
- https://github.com/langchain-ai/langgraphjs/pull/2397
- https://github.com/langchain-ai/langgraphjs/commit/284226c7ca164b3c81fe2d9e32b10f1fc6b99a3c
- https://github.com/langchain-ai/langgraphjs
