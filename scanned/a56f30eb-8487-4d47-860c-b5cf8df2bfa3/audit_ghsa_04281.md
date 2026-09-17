# [H] Budibase has an Account Impersonation Issue — Chat Identity Link Hijacking via Missing Consent & CSRF

## Summary
Severity: High
Advisory: GHSA-v7j5-vc4m-723w
CVE: CVE-2026-50132
CWE: CWE-284, CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-v7j5-vc4m-723w
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.0

## Details
## Title

**Chat Identity Link Hijacking — Attacker Can Silently Map Their Slack/Discord Identity to Any Authenticated Budibase User's Account**

## Severity

**High** — CVSS 3.1: AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N = **7.3**

## Affected Product

- **Product:** Budibase
- **Version:** 3.37.2 (introduced in this version)
- **Component:** `packages/server/src/api/controllers/ai/chatIdentityLinks.ts`
- **Endpoint:** `GET /api/chat-links/:instance/:token/handoff`


## Vulnerability Type

- CWE-352: Cross-Site Request Forgery
- CWE-284: Improper Access Control

---

## Vulnerability Description

`GET /api/chat-links/:instance/:token/handoff` is a **public endpoint** (no auth required) that performs a permanent, state-changing operation: it binds an external chat identity (Slack/Discord/MS Teams) to an authenticated Budibase user account, with **no consent UI and no CSRF protection**.

The session token in the URL is created **by the attacker** (from their own `/link` slash command) and embeds **the attacker's `externalUserId`**. When an authenticated Budibase victim visits the URL, their account is silently and permanently linked to the attacker's Slack/Discord identity. The server responds with `"Authentication succeeded."` — no indication of what was linked.

### Route Registration

```typescript
// packages/server/src/api/routes/chat.ts:22
router.get(
  "/api/chat-links/:instance/:token/handoff",
  controller.handoffChatLinkSession   // registered in publicRoutes — zero auth middleware
)
```

### Vulnerable Controller (full function)

```typescript
// packages/server/src/api/controllers/ai/chatIdentityLinks.ts:61–110
export async function handoffChatLinkSession(
  ctx: UserCtx<void, string, { instance: string; token: string }>
) {
  const token = resolveToken(ctx.params.token)
  const session = await sdk.ai.chatIdentityLinks.getChatIdentityLinkSession(token)
  if (!session) {
    throw new HTTPError("Link token is invalid or has expired", 400)
  }
  assertSessionMatchesInstance({ workspaceId: session.workspaceId, instance: ctx.params.instance })

  if (!ctx.isAuthenticated) {
    // Unauthenticated: set return URL cookie, redirect to login
    // After login, same URL is visited again → attack completes silently
    utils.setCookie(ctx,
      `/api/chat-links/${ctx.params.instance}/${token}/handoff`,
      "budibase:returnurl",
      { sign: false }  // ← unsigned cookie, but not an open redirect
    )
    ctx.redirect("/builder/auth/login")
    return
  }

  const currentGlobalUserId = getCurrentGlobalUserId(ctx)
  const consumedSession = await sdk.ai.chatIdentityLinks.consumeChatIdentityLinkSession(token)

  // ↓↓↓ THE VULNERABLE WRITE — no consent check, no CSRF token ↓↓↓
  await sdk.ai.chatIdentityLinks.upsertChatIdentityLink({
    provider: consumedSession.provider,
    externalUserId: consumedSession.externalUserId,  // ← ATTACKER's Slack ID
    externalUserName: consumedSession.externalUserName,
    teamId: consumedSession.teamId,
    globalUserId: currentGlobalUserId,   // ← VICTIM's Budibase user ID
    linkedBy: currentGlobalUserId,
  })

  ctx.type = "text/html"
  ctx.body = renderLinkSuccessPage()  // ← "Authentication succeeded." — no disclosure to user
}
```

--

---

### Step 1 — Attacker triggers `/link` in Slack

Attacker types `/link` to the Budibase Slack bot. Budibase server creates a Redis session:

**Redis key:** `chatIdentityLinkSession:tok_xxxxxxxxxxxxxxxx`

**Redis value (exact structure from `ChatIdentityLinkSession` interface):**
```json
{
  "token": "tok_xxxxxxxxxxxxxxxx",
  "tenantId": "acme",
  "workspaceId": "ws_abc123",
  "provider": "slack",
  "externalUserId": "UA12345678",
  "externalUserName": "attacker",
  "teamId": "T_ACME_SLACK",
  "createdAt": "2026-05-02T10:00:00.000Z",
  "expiresAt": "2026-05-02T10:10:00.000Z"
}
```

Slack DM sent privately to attacker:
```
Link your Slack account to continue chatting with this agent.
https://budibase.company.com/api/chat-links/ws_abc123/tok_xxxxxxxxxxxxxxxx/handoff
```

**Key observation:** This URL embeds the attacker's own `externalUserId` inside the token. The attacker has full control over which identity gets linked.

---

### Step 2 — Attacker forwards URL to victim

Attacker posts in the company Slack:
```
@admin please click this to connect your Budibase account for AI agent access:
https://budibase.company.com/api/chat-links/ws_abc123/tok_xxxxxxxxxxxxxxxx/handoff
```

---

### Step 3 — Victim clicks link (authenticated)

**HTTP Request (victim's browser):**
```http
GET /api/chat-links/ws_abc123/tok_xxxxxxxxxxxxxxxx/handoff HTTP/1.1
Host: budibase.company.com
Cookie: budibase:session=VICTIM_SESSION
```

**HTTP Response:**
```http
HTTP/1.1 200 OK
Content-Type: text/html

<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Authentication succeeded</title>
  </head>
  <body>
    <p>Authentication succeeded.</p>
    <script>
      if (window.opener && !window.opener.closed) {
        try { window.opener.focus(); window.close() } catch (error) {}
      }
    </script>
  </body>
</html>
```

The victim sees "Authentication succeeded." with no mention of Slack, no mention of `attacker`, no mention of what capabilities were granted.

**CouchDB global-db document written immediately after (exact structure from `upsertChatIdentityLink`):**

```json
{
  "_id": "chatidentitylink_acme_slack_T_ACME_SLACK_UA12345678",
  "tenantId": "acme",
  "provider": "slack",
  "externalUserId": "UA12345678",
  "globalUserId": "ro_global_us_VICTIM_ADMIN_ID",
  "linkedAt": "2026-05-02T10:00:42.000Z",
  "linkedBy": "ro_global_us_VICTIM_ADMIN_ID",
  "externalUserName": "attacker",
  "teamId": "T_ACME_SLACK",
  "createdAt": "2026-05-02T10:00:42.000Z",
  "updatedAt": "2026-05-02T10:00:42.000Z"
}
```

The mapping is now permanent. `externalUserId = UA12345678` (attacker) → `globalUserId = ro_global_us_VICTIM_ADMIN_ID` (victim).

---

### Step 4 — Attacker impersonates victim via AI agent

Attacker sends any message to the Budibase Slack bot from their own account (`UA12345678`).

The chat handler resolves the identity:

```typescript
// packages/server/src/api/controllers/webhook/chatHandler.ts:421
const existingLink = await sdk.ai.chatIdentityLinks.getChatIdentityLink({
  provider: AgentChannelProvider.SLACK,
  externalUserId: "UA12345678",     // ← attacker's Slack ID
  teamId: "T_ACME_SLACK",
})
// existingLink.globalUserId = "ro_global_us_VICTIM_ADMIN_ID"

const linkedUser = await getGlobalUser("ro_global_us_VICTIM_ADMIN_ID")
// All agent tool calls now execute with victim admin's permissions
```

The attacker can now ask the agent:

> "Show me all rows in the Customers table"
> "Trigger the 'Send Invoice' automation for customer ID 42"
> "What files are in the knowledge base?"

Each request runs with the victim admin's identity and permissions. The victim has no indication this is happening.

---

### Step 3b — Variant: Victim Not Yet Authenticated

If the victim is not currently logged in when they click the URL:

**HTTP Request:**
```http
GET /api/chat-links/ws_abc123/tok_xxxxxxxxxxxxxxxx/handoff HTTP/1.1
Host: budibase.company.com
```

**HTTP Response:**
```http
HTTP/1.1 302 Found
Location: /builder/auth/login
Set-Cookie: budibase:returnurl=%2Fapi%2Fchat-links%2Fws_abc123%2Ftok_xxxxxxxxxxxxxxxx%2Fhandoff; Path=/
```

After the victim logs in, the browser follows the return URL and the attack completes identically to Step 3.

---

---

## Remediation

### Minimum Fix — Add Consent Page

Convert the handoff to a two-step flow:

```
GET  /api/chat-links/:instance/:token/handoff
  → Show consent page: "You are linking your Budibase account to
    [externalUserName]'s Slack identity ([provider]).
    This allows them to interact with AI agents as you. [Confirm] [Cancel]"

POST /api/chat-links/:instance/:token/handoff  (with CSRF token)
  → Perform the upsertChatIdentityLink() write
```

Moving the write to `POST` removes it from `publicRoutes`, making Budibase's existing CSRF middleware apply automatically.


---
Credits,
Vishal Kumar B
https://github.com/VishaaLlKumaaRr

## References

- `packages/server/src/api/routes/chat.ts:22` — public route registration
- `packages/server/src/api/controllers/ai/chatIdentityLinks.ts:61–110` — full vulnerable controller
- `packages/server/src/sdk/workspace/ai/chatIdentityLinks.ts:135–165` — session creation (embeds attacker's externalUserId)
- `packages/server/src/sdk/workspace/ai/chatIdentityLinks.ts:202–247` — upsertChatIdentityLink (permanent write)
- `packages/server/src/api/controllers/webhook/chatHandler.ts:421` — identity resolution during agent message handling
- `packages/server/src/ai/tools/budibase/automations.ts` — automation trigger capability
- `packages/server/src/ai/tools/budibase/rows.ts` — row read/write capability
- `packages/types/src/sdk/chatIdentityLinks.ts` — session + link type definitions
- CWE-352: Cross-Site Request Forgery
- CWE-284: Improper Access Control

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-v7j5-vc4m-723w
- https://nvd.nist.gov/vuln/detail/CVE-2026-50132
- https://github.com/Budibase/budibase/pull/18793
- https://github.com/Budibase/budibase/commit/cf66fb45d27402bace312d85616ddd4257f3a5aa
- https://github.com/Budibase/budibase
