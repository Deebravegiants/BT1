# [H] Authorizer: CQL/N1QL Injection in Cassandra and Couchbase Backends via fmt.Sprintf String Interpolation

## Summary
Severity: High
Advisory: GHSA-jfwg-rxf3-p7r9
CWE: CWE-209, CWE-943
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-jfwg-rxf3-p7r9
Type: github-advisory

## Affected
- Go: `github.com/authorizerdev/authorizer` — affected >=0 <0.0.0-20260327055742-73679faa53cd

## Details
## Vulnerability Details

**CWE:** CWE-943 - Improper Neutralization of Special Elements in Data Query Logic

All 66+ CQL queries in `internal/storage/db/cassandradb/` use `fmt.Sprintf` to interpolate user-controlled values directly into CQL query strings without parameterization.

Unauthenticated endpoints (`signup`, `login`, `forgot_password`, `magic_link_login`) pass user input directly into CQL query strings.

**Note:** This advisory covers the Cassandra CQL injection only. The Couchbase N1QL injection is tracked in a separate advisory per CVE rule 4.2.11.

## Affected Code Pattern

```go
// Before (VULNERABLE) - e.g. cassandradb/user.go
query := fmt.Sprintf("SELECT ... FROM %s WHERE email = '%s'", table, email)
err := p.db.Query(query).Scan(...)
```

## Steps to Reproduce

1. Deploy Authorizer <= 2.0.0 with Cassandra backend
2. Send a signup request with a CQL injection payload in the email field:

```bash
curl -X POST http://localhost:8080/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation { signup(params: { email: \"test'\" }) { message } }"}'
```

3. The single quote breaks out of the CQL string literal, causing a CQL parse error that leaks internal schema information
4. Crafted payloads can manipulate query logic to bypass authentication or extract data

## Affected Files (10 Cassandra files)

| Package | File | Queries Fixed |
|---------|------|--------------|
| cassandradb | user.go | 7 |
| cassandradb | otp.go | 4 |
| cassandradb | session_token.go | 19 |
| cassandradb | verification_requests.go | 4 |
| cassandradb | authenticator.go | 3 |
| cassandradb | email_template.go | 5 |
| cassandradb | webhook.go | 5 |
| cassandradb | webhook_log.go | 2 |
| cassandradb | session.go | 1 |
| cassandradb | env.go | 2 |

## Impact

An unauthenticated attacker can inject arbitrary CQL operators through the email, phone, or token parameters on public-facing endpoints (signup, login, forgot_password, magic_link_login). This enables authentication bypass and data exfiltration from the Cassandra keyspace.

## Proposed Fix

Use parameterized queries:

```go
// After (FIXED)
query := fmt.Sprintf("SELECT ... FROM %s WHERE email = ?", table)
err := p.db.Query(query, email).Scan(...)
```

Fixed in https://github.com/authorizerdev/authorizer/pull/500 (merged 2026-03-27).

## References
- https://github.com/authorizerdev/authorizer/security/advisories/GHSA-jfwg-rxf3-p7r9
- https://github.com/authorizerdev/authorizer/pull/500
- https://github.com/authorizerdev/authorizer/commit/73679faa53cd215c7524d651046e402c43809786
- https://github.com/authorizerdev/authorizer
- https://github.com/authorizerdev/authorizer/releases/tag/2.0.1
