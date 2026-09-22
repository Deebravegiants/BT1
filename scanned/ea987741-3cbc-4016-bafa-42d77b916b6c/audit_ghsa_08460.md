# [H] FlowiseAI: Dataset create+update mass-assignment allows cross-workspace dataset takeover

## Summary
Severity: High
Advisory: GHSA-5h9v-837x-m97r
CVE: CVE-2026-46477
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-5h9v-837x-m97r
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.2

## Details
## Summary

**Type:** Mass assignment via `Object.assign(entity, body)` -> client-controlled `workspaceId` (and on create, `id`) overwritten on the Dataset entity -> cross-workspace data takeover and IDOR.
**File:** `packages/server/src/services/dataset/index.ts`
**Root cause:** The Dataset controller/service constructs a `new Dataset()` and copies the request body into it via `Object.assign(...)` without an explicit field allowlist. The request body therefore can include `workspaceId`, `id`, `createdDate`, `updatedDate`. The server only rebinds *some* of these after the assign (e.g. on create, it overwrites `workspaceId` but not `id`; on update, it overwrites `id` but not `workspaceId`). The remaining client-controlled values land directly on the persisted row, breaking workspace isolation. Same root pattern as the dataset entity's sibling controllers and as `DocumentStore` before it was patched in commit 840d2ae.

## Affected Code

**File:** `packages/server/src/services/dataset/index.ts`

```ts
// create (line 203) and update (line 226)
Object.assign(newDataset, body)         // <-- BUG: body.id, body.workspaceId accepted
```

**Why it's wrong:** `Object.assign(target, source)` copies every own enumerable property of `source` onto `target`. The TypeORM/SQL persistence layer below it does not strip ownership-bearing columns, so `workspaceId` set in the request body lands as the new `workspaceId` of the persisted row. The DocumentStore patch (commit 840d2ae) demonstrated the intended fix shape (explicit field-by-field allowlist) but it has not been applied to this entity.

## Exploit Chain

1. Attacker is an authenticated member of workspace A. They have a session cookie / JWT for the Flowise web UI. State at this point: attacker can read and write entities scoped to workspace A.
2. Attacker creates a dataset in workspace A via the documented API (or reuses an existing one they own). They note its entity `id`.
3. Attacker issues a `PUT /api/v1/datasets/<id>` (or equivalent endpoint) with a JSON body that includes `"workspaceId": "<workspace-B-id>"` (an arbitrary other workspace's UUID). State at this point: the request reaches the controller as a workspace-A authenticated request.
4. The controller calls `Object.assign(updateEntity, body)`. The body's `workspaceId` overwrites the entity's `workspaceId` field. The persistence layer commits the row.
5. Final state: the dataset row is now owned by workspace B. Workspace B members can see it, modify it, and use it. Workspace A loses access (it no longer satisfies their workspace filter). The original creator's workspace audit shows nothing because the operation looked like a normal update.

## Security Impact

**Severity:** High. Cross-workspace boundary violation by any authenticated workspace member.
**Attacker capability:** Any authenticated user with permission to update a dataset can move it to any workspace whose UUID they can guess or enumerate (workspace UUIDs are exposed in many API responses, so enumeration is trivial). Datasets hold training / evaluation data scoped to a workspace. Moving a Dataset across workspaces via `workspaceId` overwrite exposes the dataset (rows, schema, references) to the destination workspace.
**Preconditions:** Authenticated session with edit permission for the source dataset. No second factor required. Workspace UUIDs are exposed via the `/api/v1/workspaces` listing or via any cross-referenced object's `workspaceId` field, so target enumeration is trivial.
**Differential:** PoC-verified by source inspection of the original GHSA-q4pr-4r26-c69r. Patched build (with the suggested fix below) refuses the `workspaceId` field; vulnerable build accepts it and persists it.

## Suggested Fix

Already fixed in PR https://github.com/FlowiseAI/Flowise/pull/6051 (allowlist pattern applied).

```ts
// Allowlist pattern (matches commit 840d2ae for DocumentStore):
const updatedDataset = new Dataset()
if (body.<allowed_field_1> !== undefined) updatedDataset.<allowed_field_1> = body.<allowed_field_1>
if (body.<allowed_field_2> !== undefined) updatedDataset.<allowed_field_2> = body.<allowed_field_2>
// ...whitelist only the documented fields. Never copy id, workspaceId, createdDate, updatedDate from the client.
```

Regression tests should assert that a request body containing `workspaceId`, `id`, `createdDate`, or `updatedDate` is rejected (or at minimum: does not change those columns on the persisted row) for both create and update paths.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-5h9v-837x-m97r
- https://nvd.nist.gov/vuln/detail/CVE-2026-46477
- https://github.com/FlowiseAI/Flowise/pull/6051
- https://github.com/FlowiseAI/Flowise/commit/49a2259bf2a6b4f3d4b50813cb5161cee0d40040
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.2
