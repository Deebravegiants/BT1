# [H] Budibase: Webhook schema endpoint authorization bypass allows unauthenticated mutation of webhook and automation schema

## Summary
Severity: High
Advisory: GHSA-qhv3-wjg8-6fx6
CVE: CVE-2026-48151
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-qhv3-wjg8-6fx6
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.0

## Details
The webhook schema-building endpoint is registered under `builderRoutes`, but the generic authorization middleware skips authorization for all paths matching `/api/webhooks/schema`. As a result, an unauthenticated caller can update the body schema for a known webhook and mutate the corresponding automation trigger output schema.

### Details

The route appears to be builder-only:

- `packages/server/src/api/routes/webhook.ts:5-9`

```ts
5:builderRoutes
6:  .get("/api/webhooks", controller.fetch)
7:  .put("/api/webhooks", webhookValidator(), controller.save)
8:  .delete("/api/webhooks/:id/:rev", controller.destroy)
9:  .post("/api/webhooks/schema/:instance/:id", controller.buildSchema)
```

However, webhook endpoint detection explicitly includes `schema`:

- `packages/server/src/middleware/utils.ts:3-9`

```ts
3:const WEBHOOK_ENDPOINTS = new RegExp(
4:  "^/api/webhooks/(trigger|schema|discord|ms-teams|slack)(/|$)"
5:)
6:
7:export function isWebhookEndpoint(ctx: UserCtx): boolean {
8:  const path = ctx.path || ctx.request.url.split("?")[0]
9:  return WEBHOOK_ENDPOINTS.test(path)
```

The authorization middleware bypasses all webhook endpoints before checking `ctx.user` or permissions:

- `packages/server/src/middleware/authorized.ts:90-99`

```ts
90:  ) =>
91:  async (ctx: UserCtx, next: any) => {
92:    // webhooks don't need authentication, each webhook unique
93:    // also internal requests (between services) don't need authorized
94:    if (isWebhookEndpoint(ctx) || ctx.internal) {
95:      return next()
96:    }
97:
98:    if (!ctx.user) {
99:      return ctx.throw(401, "No user info found")
```

The bypassed controller writes attacker-derived schema data to the webhook and automation trigger outputs:

- `packages/server/src/api/controllers/webhook.ts:56-83`

```ts
56:export async function buildSchema(
57:  ctx: Ctx<BuildWebhookSchemaRequest, BuildWebhookSchemaResponse>
58:) {
59:  await context.doInWorkspaceContext(ctx.params.instance, async () => {
60:    const db = context.getWorkspaceDB()
61:    const webhook = await db.get<Webhook>(ctx.params.id)
62:    webhook.bodySchema = toJsonSchema(ctx.request.body)
63:    // update the automation outputs
64:    if (webhook.action.type === WebhookActionType.AUTOMATION) {
65:      let automation = await db.get<Automation>(webhook.action.target)
66:      const autoOutputs = automation.definition.trigger.schema.outputs
67:      let properties = webhook.bodySchema?.properties
68:      // reset webhook outputs
69:      autoOutputs.properties = {
70:        body: autoOutputs.properties.body,
71:      }
72:      for (let prop of Object.keys(properties || {})) {
73:        if (properties?.[prop] == null) {
74:          continue
75:        }
76:        const def = properties[prop]
77:        if (typeof def === "boolean") {
78:          continue
79:        }
80:        autoOutputs.properties[prop] = {
81:          type: def.type as AutomationIOType,
82:          description: AUTOMATION_DESCRIPTION,
83:        }
```

The route grouping suggests builder authorization was intended, but the global webhook bypass removes it.

### PoC

Non-destructive validation approach:

1. Create a webhook-backed automation as a builder.
2. Record the workspace ID and webhook ID.
3. Log out or send no auth headers.
4. Send:

```http
POST /api/webhooks/schema/<workspaceId>/<webhookId> HTTP/1.1
content-type: application/json

{"unauth_schema_probe":"test"}
```

5. Fetch the webhook as a builder and observe that `bodySchema` has changed.
6. For automation-backed webhooks, inspect the automation trigger schema outputs and observe that properties were reset/updated.

### Impact

An unauthenticated attacker can modify webhook schema metadata and automation trigger output schema for known webhook IDs. This can corrupt builder-visible automation definitions, alter downstream binding behavior, and disrupt webhook-backed automation workflows.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-qhv3-wjg8-6fx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-48151
- https://github.com/Budibase/budibase
