# [M] LangGraph: BaseCache Deserialization of Untrusted Data may lead to Remote Code Execution 

## Summary
Severity: Medium
Advisory: GHSA-mhr3-j7m5-c7c9
CVE: CVE-2026-27794
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-mhr3-j7m5-c7c9
Type: github-advisory

## Affected
- PyPI: `langgraph-checkpoint` — affected >=0 <4.0.0

## Details
## Context

A Remote Code Execution vulnerability exists in LangGraph's caching layer when applications enable cache backends that inherit from `BaseCache` and opt nodes into caching via `CachePolicy`. Prior to `langgraph-checkpoint` 4.0.0, `BaseCache` defaults to `JsonPlusSerializer(pickle_fallback=True)`. When msgpack serialization fails, cached values can be deserialized via `pickle.loads(...)`.

### Who is affected?

Caching is not enabled by default. Applications are affected only when:

- The application explicitly enables a cache backend (for example by passing `cache=...` to `StateGraph.compile(...)` or otherwise configuring a `BaseCache` implementation)
- One or more nodes opt into caching via `CachePolicy`
- The attacker can write to the cache backend (for example a network-accessible Redis instance with weak/no auth, shared cache infrastructure reachable by other tenants/services, or a writable SQLite cache file)

Example (enabling a cache backend and opting a node into caching):

```py
from langgraph.cache.memory import InMemoryCache
from langgraph.graph import StateGraph
from langgraph.types import CachePolicy


def my_node(state: dict) -> dict:
    return {"value": state.get("value", 0) + 1}


builder = StateGraph(dict)
builder.add_node("my_node", my_node, cache_policy=CachePolicy(ttl=120))
builder.set_entry_point("my_node")

graph = builder.compile(cache=InMemoryCache())

result = graph.invoke({"value": 1})
```

With `pickle_fallback=True`, when msgpack serialization fails, `JsonPlusSerializer` can fall back to storing values as a `("pickle", <bytes>)` tuple and later deserialize them via `pickle.loads(...)`. If an attacker can place a malicious pickle payload into the cache backend such that the LangGraph process reads and deserializes it, this can lead to arbitrary code execution.

Exploitation requires attacker write access to the cache backend. The serializer is not exposed as a network-facing API.

This is fixed in `langgraph-checkpoint>=4.0.0` by disabling pickle fallback by default (`pickle_fallback=False`).

## Impact

Arbitrary code execution in the LangGraph process when attacker-controlled cache entries are deserialized.

## Root Cause

- `BaseCache` default serializer configuration inherited by cache implementations (`InMemoryCache`, `RedisCache`, `SqliteCache`):
  - `libs/checkpoint/langgraph/cache/base/__init__.py` (pre-fix default: `JsonPlusSerializer(pickle_fallback=True)`)

- `JsonPlusSerializer` deserialization sink:
  - `libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py`
  - `loads_typed(...)` calls `pickle.loads(data_)` when `type_ == "pickle"` and pickle fallback is enabled

## Attack preconditions

An attacker must be able to write attacker-controlled bytes into the cache backend such that the LangGraph process later reads and deserializes them.

This typically requires write access to a networked cache (for example a network-accessible Redis instance with weak/no auth or shared cache infrastructure reachable by other tenants/services) or write access to local cache storage (for example a writable SQLite cache file via permissive file permissions or a shared writable volume).

Because exploitation requires write access to the cache storage layer, this is a post-compromise / post-access escalation vector.

## Remediation

- Upgrade to `langgraph-checkpoint>=4.0.0`.

## Resources

- ZDI-CAN-28385
- Patch: https://github.com/langchain-ai/langgraph/pull/6677
- Patch diff: https://patch-diff.githubusercontent.com/raw/langchain-ai/langgraph/pull/6677.patch
- Credit: Peter Girnus (@gothburz), Demeng Chen, and Brandon Niemczyk (Trend Micro Zero Day Initiative)

## References
- https://github.com/langchain-ai/langgraph/security/advisories/GHSA-mhr3-j7m5-c7c9
- https://nvd.nist.gov/vuln/detail/CVE-2026-27794
- https://github.com/langchain-ai/langgraph/pull/6677
- https://github.com/langchain-ai/langgraph/commit/f91d79d0c86932ded6e3b9f195d5a0bbd5aef99c
- https://github.com/langchain-ai/langgraph
- https://github.com/langchain-ai/langgraph/releases/tag/checkpoint%3D%3D4.0.0
