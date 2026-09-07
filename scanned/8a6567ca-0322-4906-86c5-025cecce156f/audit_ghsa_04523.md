# [H] Budibase: Mass Assignment in Webhook Trigger Allows Cross-Workspace Automation Execution via appId Override

## Summary
Severity: High
Advisory: GHSA-rgvg-3wpc-h44p
CVE: CVE-2026-54351
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-rgvg-3wpc-h44p
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.9

## Details
## Summary

The webhook trigger endpoint in Budibase is publicly accessible and passes the full HTTP request body into automation execution parameters. A mass assignment vulnerability in `externalTrigger()` allows an attacker to overwrite the internal `appId` property by including it in the webhook POST body. When the automation is processed asynchronously (the default path for webhooks without a collect step), the worker executes the attacker-defined automation in the context of the victim's workspace, granting full read/write access to the victim's database.

## Details

The webhook trigger route is registered as a public endpoint with no authentication:

```typescript
// packages/server/src/api/routes/webhook.ts:12
publicRoutes.post("/api/webhooks/trigger/:instance/:id", controller.trigger)
```

The controller passes the raw request body as `fields` alongside the server-derived `appId`:

```typescript
// packages/server/src/api/controllers/webhook.ts:142-148
await triggers.externalTrigger(target, {
  fields: {
    ...ctx.request.body,  // attacker-controlled
    body: ctx.request.body,
  },
  appId: prodAppId,       // server-controlled
})
```

In `externalTrigger()`, for webhook-triggered automations, `params.fields` is spread back into `params`:

```typescript
// packages/server/src/automations/triggers.ts:237-241
params = {
  ...params,          // appId: prodAppId (server-controlled)
  ...params.fields,   // appId: VICTIM_ID (attacker-controlled, overwrites above)
  fields: {},
}
```

Because `params.fields` is spread **after** `params`, any key in the attacker's body overwrites the corresponding property in `params`. An attacker including `"appId": "app_VICTIM_WORKSPACE_ID"` in the POST body overwrites the legitimate, server-derived `appId`.

The contaminated params become `data.event` and are queued asynchronously:

```typescript
// packages/server/src/automations/triggers.ts:244,271
const data: AutomationData = { automation, event: params }
// ...
return quotas.addAction(() => automationQueue.add(data, JOB_OPTS))
```

The async worker uses `job.data.event.appId` to set the workspace context:

```typescript
// packages/server/src/threads/automation.ts:917,929-930
const workspaceId = job.data.event.appId  // attacker-controlled
// ...
return await context.doInAutomationContext({
  workspaceId,  // victim's workspace
  automationId,
  task: async () => { /* automation steps run here */ }
})
```

The synchronous path (for webhooks with a collect step) correctly overwrites `appId` at `triggers.ts:264`:
```typescript
data.event = {
  ...data.event,
  appId: context.getWorkspaceId(),  // server-controlled fix
  automation,
}
```

This proves the developers intended `appId` to be server-controlled but missed applying the same fix to the async path, which is the default for all webhooks without a collect step.

## PoC

**Prerequisites:** Attacker has builder access to their own Budibase workspace and knows a victim workspace ID (format: `app_<uuid>`).

**Step 1:** Attacker creates an automation in their own workspace with a webhook trigger and data-exfiltration steps (e.g., Query Rows → Execute Script to send data externally).

**Step 2:** Attacker creates a webhook for that automation and notes the webhook URL:
```
POST /api/webhooks/trigger/<ATTACKER_INSTANCE>/<WEBHOOK_ID>
```

**Step 3:** Attacker triggers the webhook with the victim's workspace ID injected into the body:

```bash
curl -X POST https://budibase.example.com/api/webhooks/trigger/app_ATTACKER_ID/wh_WEBHOOK_ID \
  -H 'Content-Type: application/json' \
  -d '{"appId": "app_VICTIM_WORKSPACE_ID", "normalData": "test"}'
```

**Expected result:** The automation defined in the attacker's workspace executes in the context of the victim's workspace. All database operations (Query Rows, Create Row, Delete Row, Execute Script, etc.) operate on the victim's data.

**Additional overridable fields via the same mechanism:**
- `timeout` (`automation.ts:443-444`): override automation execution timeout
- `user` (`automation.ts:413,435`): set user context for automation steps
- `metadata.automationChainCount` (`automation.ts:293`): bypass chain depth limits

## Impact

An attacker with builder access to their own Budibase workspace can execute arbitrary automations (of their own design) in the context of any other workspace on the same Budibase instance, provided they know the victim's workspace ID. This enables:

- **Full data exfiltration**: Query Rows steps read all tables in the victim's workspace
- **Data manipulation**: Create Row, Update Row, Delete Row steps modify victim data
- **Arbitrary code execution in victim context**: Execute Script steps run JavaScript with access to victim's environment variables and database
- **Cross-tenant boundary violation**: In multi-tenant deployments (Budibase Cloud), the tenant ID is derived from the workspace ID, so the attack crosses tenant boundaries

The attack requires no authentication (the webhook endpoint is public) and leaves minimal audit trail since the automation execution is attributed to the attacker's automation definition but runs in the victim's context.

## Recommended Fix

In `packages/server/src/automations/triggers.ts`, apply the same `appId` fix that exists in the synchronous path to the async path as well. The fix should ensure `appId` is always server-controlled before queuing:

```typescript
// packages/server/src/automations/triggers.ts:244-272
const data: AutomationData = { automation, event: params }

// ... trigger filter check ...

+ // Ensure appId is always server-controlled, not user-supplied
+ data.event.appId = context.getWorkspaceId()

if (getResponses) {
  data.event = {
    ...data.event,
    appId: context.getWorkspaceId(),
    automation,
  }
  return quotas.addAction(() =>
    executeInThread({ data } as AutomationJob, { onProgress })
  )
} else {
  return quotas.addAction(() => automationQueue.add(data, JOB_OPTS))
}
```

Alternatively, use an allowlist approach for the webhook field spread to prevent any internal property from being overwritten:

```typescript
// packages/server/src/automations/triggers.ts:237-241
const { appId, timeout, user, metadata, ...safeFields } = params.fields
params = {
  ...params,
  ...safeFields,
  fields: {},
}
```

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-rgvg-3wpc-h44p
- https://nvd.nist.gov/vuln/detail/CVE-2026-54351
- https://github.com/Budibase/budibase
