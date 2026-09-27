# [H] LangGraph's SQLite is vulnerable to SQL injection via metadata filter key in SQLite checkpointer list method

## Summary
Severity: High
Advisory: GHSA-9rwj-6rc7-p77c
CVE: CVE-2025-67644
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-9rwj-6rc7-p77c
Type: github-advisory

## Affected
- PyPI: `langgraph-checkpoint-sqlite` — affected >=0 <3.0.1

## Details
# Context

A SQL injection vulnerability exists in LangGraph's SQLite checkpoint implementation that allows attackers to manipulate SQL queries through metadata filter keys. This affects applications that accept **untrusted metadata filter keys** (not just filter values) in checkpoint search operations.

# Impact

Attackers who control metadata filter keys can execute arbitrary sql queries against the database.

# Root Cause

The `_metadata_predicate()` function constructs SQL queries by interpolating filter keys directly into f-strings without validation:

```python
# VULNERABLE CODE (before fix)
for query_key, query_value in metadata_filter.items():
    operator, param_value = _where_value(query_value)
    predicates.append(
        f"json_extract(CAST(metadata AS TEXT), '$.{query_key}') {operator}"
    )
    param_values.append(param_value)
```

While filter **values** are parameterized, filter **keys** are not validated, allowing SQL injection.

# Attack Example

**Before Fix:**
```python
from langgraph.checkpoint.sqlite import SqliteSaver

saver = SqliteSaver.from_conn_string("checkpoints.db")

# Attacker controls the filter keys
malicious_filter = {"x') OR '1'='1": "dummy"}

# Returns ALL checkpoints, bypassing filtering
results = list(saver.list(None, filter=malicious_filter))
```

**Resulting SQL:**
```sql
WHERE json_extract(CAST(metadata AS TEXT), '$.x') OR '1'='1') = ?
-- Injected condition makes WHERE clause always true
```

## Who Is Affected?

### LangSmith Deployment Customers: NOT Impacted

**LangSmith deployment customers are NOT affected by this vulnerability.** LangSmith deployments do not allow configuring custom checkpointers, so the vulnerable code path cannot be reached.

### High Risk: Custom Server Deployments

You are affected if your application:
- Runs a custom server with SqliteSaver checkpointer
- Exposes an endpoint for fetching checkpoint history (e.g., via `get_state_history()`)
- Accepts metadata filter keys from untrusted sources

**Example vulnerable code:**
```python
# Custom server endpoint - User controls filter key names - DANGEROUS
@app.post("/api/history")
def get_history(request):
    filter_field = request.json.get("filter_field")  # Untrusted input
    filter_value = request.json.get("filter_value")

    # VULNERABLE: Attacker can bypass access controls
    history = list(graph.get_state_history(
        config,
        filter={filter_field: filter_value}
    ))
    return history
```

**Note on privilege escalation:** If an endpoint allows end users to specify arbitrary filter keys, those users likely already have legitimate access to query the checkpoint database. In such cases, this vulnerability may not constitute a privilege escalation, as users who can control filter keys would typically already be expected to have database access. However, the SQL injection still allows bypassing intended filtering logic and metadata-based access controls that the application may rely on for data isolation.

### Additional Security Hardening (Defense in Depth)

This release also includes hardening improvements:

**1. Checkpoint Limit Parameter**: used f-string interpolation into parameterized query.  Not considered a vulnerability as it requires users to accept untrusted input and not validate it against the actual API signature. 

**2. Store Filter Value Parameterization**: Refactored all filter value handling from manual quote escaping to parameterized queries

## Remediation

### Immediate Actions

1. **Update to the patched version** of `langgraph-checkpoint-sqlite`
2. **Audit your code** for locations where filter keys come from untrusted sources

## References
- https://github.com/langchain-ai/langgraph/security/advisories/GHSA-9rwj-6rc7-p77c
- https://nvd.nist.gov/vuln/detail/CVE-2025-67644
- https://github.com/langchain-ai/langgraph/commit/297242913f8ad2143ee3e2f72e67db0911d48e2a
- https://github.com/langchain-ai/langgraph
