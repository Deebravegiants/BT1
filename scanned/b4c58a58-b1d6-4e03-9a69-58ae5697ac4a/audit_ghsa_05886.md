# [H] Trigger.dev: Prototype pollution via run metadata operations → process-wide cross-tenant DoS

## Summary
Severity: High
Advisory: GHSA-p28v-f755-9qrg
CVE: CVE-2026-73654
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H (CVSS_V3)
Published: 2026-08-13
Source: https://github.com/advisories/GHSA-p28v-f755-9qrg
Type: github-advisory

## Affected
- npm: `@trigger.dev/core` — affected >=3.3.8 <4.5.6

## Details
## Summary

The run-metadata update endpoint `PUT /api/v1/runs/:runId/metadata` applies client-supplied
"operations" by passing the **attacker-controlled `operation.key`** straight into
`new JSONHeroPath(operation.key).set(newMetadata, value)`
(`packages/core/src/v3/runMetadata/operations.ts:22-23`), with **no prototype-pollution guard**
(`@jsonhero/path@^1.0.21` does not reject `__proto__`/`constructor`/`prototype`).

A request with `key: "$.__proto__.polluted"` sets **`Object.prototype.polluted`** in the webapp
process. Because every plain object then inherits that property, it corrupts unrelated code
**process-wide and across tenants** — including Prisma query building and the Prometheus metrics
client — causing query failures, **broken authentication for other tenants' workers**, and an
`uncaughtException` (denial of service). Only a normal, low-privilege environment API key is
required (one request).

## Severity

A single request from any holder of a normal environment API key contaminates `Object.prototype`
in the shared webapp process, breaking other tenants' workers (scope change) and degrading/
crashing the process (high availability impact). Prototype pollution is also a primitive for
further gadget chains (integrity/confidentiality).

## Affected versions

- **Introduced** in commit `34f8bd588` ("Add ability to update parent and root run metadata from
  children", PR #1563, 2025-01-08) — the `JSONHeroPath(operation.key).set()` sink is present from
  the first commit of `operations.ts`. SDK was at `3.3.8` at that time.
- **Still present at HEAD** (SDK `4.5.0-rc.7`); `operations.ts` unchanged since 2025-05, and
  `@jsonhero/path` is pinned at `^1.0.21` (no proto-guard) throughout.
- **Affected range:** `>= v3.3.8` (metadata operations API) through `v4-beta` / current v4.x —
  **fixed: 4.5.6**.

## Root cause

`packages/core/src/v3/runMetadata/operations.ts` — `applyMetadataOperations()` builds a path from
the **untrusted** `operation.key` and writes to it, for every operation type (`set`, `append`,
`increment`, …):

```ts
const path = new JSONHeroPath(operation.key);   // operation.key fully attacker-controlled
path.set(newMetadata, operation.value);         // no __proto__/constructor/prototype rejection
```

The request schema (`UpdateMetadataRequestBody`) types `key` as a plain string with no validation,
and `@jsonhero/path@1.0.21` walks `__proto__` as an ordinary segment → the assignment lands on
`Object.prototype`.

## Proof of Concept

Self-host `ghcr.io/triggerdotdev/trigger.dev:v4-beta`. Authenticated with a **normal environment
API key** (`tr_dev_…`) and any run id of that environment.

```bash
curl -X PUT "http://localhost:8030/api/v1/runs/run_cmqr2bsyo00013js2twwhdsfu/metadata" \
  -H "Authorization: Bearer tr_dev_<env_key>" -H "Content-Type: application/json" \
  --data '{"operations":[{"type":"set","key":"$.__proto__.polluted","value":"PWNED"}]}'
```

**Result — `Object.prototype.polluted = "PWNED"` process-wide.** Observed in the webapp logs:

1. **The request's own query is corrupted** — `polluted:"PWNED"` injected into every object Prisma
   enumerates:
   ```
   prisma.taskRun.updateMany({ where:{ id:"…", metadataVersion:2, polluted:"PWNED" },
     data:{ …, metadataVersion:{ increment:1, polluted:"PWNED" }, polluted:"PWNED" }, polluted:"PWNED" })
   -> Unknown argument `polluted`
   ```
2. **Cross-tenant authentication break** — the *next* request from a different client (a worker's
   `POST /engine/v1/dev/dequeue`) fails inside `findEnvironmentByApiKey`:
   ```
   prisma.runtimeEnvironment.findFirst({ where:{ apiKey:"…", polluted:"PWNED" },
     include:{ project:true, …, polluted:"PWNED" } })  -> PrismaClientValidationError
   ```
   i.e. one tenant's request **breaks authentication for other tenants' workers** → their jobs stop
   being dequeued/processed.
3. **Denial of service — full process crash.** The `uncaughtException` in prom-client
   (`Error: Added label "polluted" is not included in initial labelset: [ 'kind' ]`) **crashes the
   webapp process**. Demonstrated with a second tenant: Tenant B (a *different* org/env, with its
   own API key) had a working request (`POST /engine/v1/dev/dequeue` → HTTP 400, auth OK) **before**
   the attack; **immediately after Tenant A's single attack request, B's request returned HTTP 000
   (no response) — the whole multi-tenant webapp was down**. Logs show the crash at 20:53:41 and the
   process auto-restarting ~3s later (`FairQueue/ScheduleEngine started`). Repeating the attack in a
   loop yields a **crash-loop = sustained DoS for all tenants**.

*(Note: the metadata endpoint itself swallows the Prisma failure with `ignoreError:true` and still
returns HTTP 200 — the damage is the process-wide contamination observed in the logs, not the
endpoint's status code.)*

## Impact

A low-privilege caller (one normal environment API key, one request) pollutes `Object.prototype`
in the shared multi-tenant webapp process, causing:

- **Full cross-tenant denial of service** — the resulting `uncaughtException` **crashes the webapp
  process**, taking the service down for **all tenants** (demonstrated: a second tenant's request
  returned HTTP 000 immediately after the attack). Repeating the request produces a **crash-loop /
  sustained DoS**. Even without the crash, contaminated Prisma queries break other tenants' worker
  authentication, halting job processing.
- **A prototype-pollution primitive** usable for further gadget chains (auth/logic bypass, etc.).

## Suggested remediation

1. **Reject dangerous path segments** in `operation.key` before building the path — block
   `__proto__`, `constructor`, `prototype` (and validate the `$.`-rooted JSONHero path shape).
2. **Build metadata on a null-prototype object** (`Object.create(null)`) and/or use a
   pollution-safe setter, so `__proto__` cannot reach `Object.prototype`.
3. Upgrade/replace `@jsonhero/path` for a version that is prototype-pollution safe, or wrap its
   `.set()` with a guard.

## References
- https://github.com/triggerdotdev/trigger.dev/security/advisories/GHSA-p28v-f755-9qrg
- https://github.com/triggerdotdev/trigger.dev/pull/4316
- https://github.com/triggerdotdev/trigger.dev/commit/6997aeb05e27d2db47f9eda01fdc8a17c81a1ae0
- https://github.com/triggerdotdev/trigger.dev
- https://github.com/triggerdotdev/trigger.dev/releases/tag/v4.5.6
