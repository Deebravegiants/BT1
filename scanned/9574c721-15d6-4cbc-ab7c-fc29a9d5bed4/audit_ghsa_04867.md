# [H] AgenticMail: Cross-agent task authorization bypass in AgenticMail API

## Summary
Severity: High
Advisory: GHSA-hjwc-26pj-v3pm
CVE: CVE-2026-57494
CWE: CWE-639, CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-hjwc-26pj-v3pm
Type: github-advisory

## Affected
- npm: `@agenticmail/api` — affected >=0 <0.9.64

## Details
## Summary

A low-privileged authenticated AgenticMail agent can enumerate another agent's pending/claimed tasks by supplying the target agent name to `GET /api/agenticmail/tasks/pending?assignee=<name>`. The returned task objects include the task IDs and payloads. The same task IDs can then be used with the capability-style task mutation endpoints (`/tasks/:id/claim`, `/tasks/:id/result`, `/tasks/:id/complete`, `/tasks/:id/fail`) to claim, complete, or fail tasks assigned to a different agent.

Because ordinary authenticated agents can discover agent names through `GET /api/agenticmail/accounts/directory`, the task ID effectively stops being a secret capability. This turns the intended capability model into a cross-agent authorization bypass.

## Affected component

Package: `@agenticmail/api`
Observed version: `0.9.62`
Repository: `agenticmail/agenticmail`

Relevant code paths:

- `packages/api/src/app.ts`: `createAuthMiddleware(...)` is mounted before `createAccountRoutes(...)` and `createTaskRoutes(...)`, so these routes are reachable by any valid bearer token.
- `packages/api/src/routes/accounts.ts`: `GET /accounts/directory` is available to any authenticated user and returns agent names.
- `packages/api/src/routes/tasks.ts`: `GET /tasks/pending?assignee=name` resolves arbitrary agent names and returns that agent's pending/claimed tasks.
- `packages/api/src/routes/tasks.ts`: `/tasks/:id/claim`, `/tasks/:id/result`, `/tasks/:id/complete`, `/tasks/:id/fail`, and `/tasks/:id` do not check whether the authenticated caller is the task assignee, assigner, or otherwise authorized for the task.

## Impact

An attacker only needs a valid agent API key. They can:

1. List agent names using `/accounts/directory`.
2. Query another agent's task queue using `/tasks/pending?assignee=<victimName>`.
3. Read sensitive task payloads intended for the victim agent.
4. Use the disclosed task ID to complete/fail/claim the victim's task or submit attacker-controlled results.

## Local reproduction

I reproduced this locally with a focused Vitest test mounted directly on `createTaskRoutes`. The test creates two agents, Alice and Bob, and one pending task assigned to Bob. Alice authenticates with her own agent key and performs the following sequence:

1. `GET /api/agenticmail/tasks/pending?assignee=Bob` with `Authorization: Bearer ak_alice`.
2. The response is HTTP 200 and includes Bob's task ID and payload: `task-for-bob`, `{ "task": "secret task intended for Bob" }`.
3. Alice then sends `POST /api/agenticmail/tasks/task-for-bob/complete` with her own bearer token and an attacker-controlled result.
4. The task status becomes `completed` and the stored result is controlled by Alice.

The local verification command was:

```bash
npm run test --workspace=@agenticmail/api -- task-routes-authz.test.ts
```

Result:

```text
PASS src/__tests__/task-routes-authz.test.ts (1 test)
```

## Expected behavior

Task listing and task mutation endpoints should enforce an authorization relationship between the authenticated caller and the task. For example:

- `GET /tasks/pending?assignee=<name>` should either be restricted to the current agent, master/admin callers, or an explicit delegated relationship.
- `/tasks/:id/claim`, `/tasks/:id/result`, `/tasks/:id/complete`, `/tasks/:id/fail`, and `/tasks/:id` should verify that the caller is the assignee, assigner, master/admin, or otherwise explicitly authorized.
- If capability-based task IDs are retained, the API should not expose those IDs to unrelated agents through the assignee-name listing path.

## Credit

Please credit the finder as: Yaohui Wang

## References
- https://github.com/agenticmail/agenticmail/security/advisories/GHSA-hjwc-26pj-v3pm
- https://github.com/agenticmail/agenticmail
