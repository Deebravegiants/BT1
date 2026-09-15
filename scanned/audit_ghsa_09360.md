# [M] Budibase: Row Action Trigger Bypasses View Row Filter Security Boundary Allowing Action on Out-of-Scope Rows

## Summary
Severity: Medium
Advisory: GHSA-3263-v5v9-xq8q
CVE: CVE-2026-45718
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-3263-v5v9-xq8q
Type: github-advisory

## Affected
- npm: `budibase` — affected >=0 <3.38.1

## Details
## Summary

The row action trigger endpoint (`POST /api/tables/:sourceId/actions/:actionId/trigger`) fails to validate that the user-supplied `rowId` is within the scope of the view's row filters. A user with access to a filtered view can trigger row actions on any row in the underlying table, including rows explicitly excluded by the view's security filters.

## Details

View filters in Budibase are treated as a security boundary. The search path (`packages/server/src/sdk/workspace/rows/search.ts:93-94`) explicitly enforces view query filters with the comment: *"that could let users find rows they should not be allowed to access."*

However, the row action trigger path bypasses this enforcement entirely:

1. **Route** (`packages/server/src/api/routes/rowAction.ts:55-59`): Accepts a `sourceId` that can be a viewId.

2. **Middleware** (`packages/server/src/middleware/triggerRowActionAuthorised.ts:24-55`): Correctly validates that the user has READ permission on the view and that the row action is enabled for that view. However, at line 55 it sets `ctx.params.tableId = tableId` where `tableId` is the **underlying table** extracted from the viewId — the viewId is discarded.

```typescript
// triggerRowActionAuthorised.ts:24-26
const tableId = isTableIdOrExternalTableId(sourceId)
  ? sourceId
  : getTableIdFromViewId(sourceId)  // extracts underlying table

// Line 55: viewId context is lost
ctx.params.tableId = tableId
```

3. **Controller** (`packages/server/src/api/controllers/rowAction/run.ts:11`): Reads only `tableId` from params — the view context is gone.

```typescript
const { tableId, actionId } = ctx.params
const { rowId } = ctx.request.body
await sdk.rowActions.run(tableId, actionId, rowId, ctx.user)
```

4. **SDK** (`packages/server/src/sdk/workspace/rowActions/crud.ts:254`): Fetches the row using `sdk.rows.find(tableId, rowId)` — directly from the table with no view filter enforcement.

```typescript
const row = await sdk.rows.find(tableId, rowId)  // No view filter check
```

The `sdk.rows.find` function (`packages/server/src/sdk/workspace/rows/internal.ts:67-88`) fetches the row by ID directly from the database, only validating that `row.tableId === tableId`. It never checks whether the row matches the view's query filters.

## PoC

```bash
# Prerequisites:
# 1. Create a table with a "status" column containing rows: "active" and "archived"
# 2. Create a view filtering to status="active", assign it to BASIC role
# 3. Enable a row action for that view
# 4. Note the rowId of an "archived" row (not visible through the view)

# As a BASIC-role user with access only to the filtered view:
# Trigger the row action on a row OUTSIDE the view's filter scope

curl -X POST 'http://localhost:10000/api/tables/<viewId>/actions/<actionId>/trigger' \
  -H 'Cookie: budibase:auth=<basic_user_jwt>' \
  -H 'Content-Type: application/json' \
  -d '{"rowId": "<archived_row_id>"}'

# Expected: 403 or 404 (row not in view scope)
# Actual: 200 {"message": "Row action triggered."}
# The automation executes with the full archived row data,
# despite view filters excluding it from the user's access.
```

## Impact

A user with BASIC role access to a filtered view can execute row actions (automations) on **any row** in the underlying table, including rows hidden by the view's security filters. The impact depends on what the triggered automation does:

- **Information disclosure**: The automation receives the full row data as input, which may contain fields/values the user should not see.
- **Unauthorized data modification**: If the automation modifies rows, the attacker can cause changes to rows outside their authorized scope.
- **Unauthorized actions**: If the automation sends notifications, calls webhooks, or performs other side effects, the attacker can trigger these for out-of-scope rows.

This breaks the security model established by view filters, which are explicitly documented as preventing users from accessing rows they should not see.

## Recommended Fix

The middleware should pass the `viewId` to the controller, and the SDK `run` function should validate the row against the view's filters before executing the automation.

In `packages/server/src/middleware/triggerRowActionAuthorised.ts`, preserve the sourceId:

```typescript
// Line 55: preserve the original sourceId for downstream filter validation
ctx.params.tableId = tableId
ctx.params.sourceId = viewId || tableId  // ADD THIS
```

In `packages/server/src/api/controllers/rowAction/run.ts`, pass the sourceId:

```typescript
export async function run(
  ctx: Ctx<RowActionTriggerRequest, RowActionTriggerResponse>
) {
  const { tableId, actionId, sourceId } = ctx.params
  const { rowId } = ctx.request.body

  await sdk.rowActions.run(tableId, actionId, rowId, ctx.user, sourceId)
  ctx.body = { message: "Row action triggered." }
}
```

In `packages/server/src/sdk/workspace/rowActions/crud.ts`, validate the row against view filters:

```typescript
export async function run(
  tableId: any,
  rowActionId: any,
  rowId: string,
  user: User,
  sourceId?: string
) {
  const table = await sdk.tables.getTable(tableId)
  if (!table) {
    throw new HTTPError("Table not found", 404)
  }

  // If triggered from a view, validate the row is within the view's scope
  if (sourceId && isViewId(sourceId)) {
    const result = await sdk.rows.search({
      viewId: sourceId,
      query: { equal: { _id: rowId } },
      limit: 1,
    })
    if (!result.rows.length) {
      throw new HTTPError("Row not found in view scope", 403)
    }
  }

  const { automationId } = await get(tableId, rowActionId)
  const automation = await sdk.automations.get(automationId)
  const row = await sdk.rows.find(tableId, rowId)
  // ... rest unchanged
}
```

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-3263-v5v9-xq8q
- https://nvd.nist.gov/vuln/detail/CVE-2026-45718
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.38.1
