# [M] eventsource-encoder vulnerable to SSE event injection via unsanitized `event` and `id` fields

## Summary
Severity: Medium
Advisory: GHSA-m9g3-3g99-mhpx
CVE: CVE-2026-44214
CWE: CWE-113, CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-m9g3-3g99-mhpx
Type: github-advisory

## Affected
- npm: `eventsource-encoder` — affected >=0 <1.0.2

## Details
### Summary

`eventsource-encoder` does not sanitize the `event` or `id` fields of an `EventSourceMessage` before serializing them. An attacker who controls either field can inject arbitrary Server-Sent Events line terminators (`\n`, `\r`, or `\r\n`) and thereby forge additional SSE fields or entire messages on the stream. This is similar in spirit to [GHSA-4hxc-9384-m385](https://github.com/advisories/GHSA-4hxc-9384-m385) (h3), but the vulnerable fields are `event`/`id` rather than `data`/`comment`. These are less likely to be user-controllable, but should still be sanitized.

### Details

In `src/encode.ts`, `encodeMessage` interpolates `event` and `id` into the output without inspecting them for line terminators:

```ts
if (message.event) {
  output += `event: ${message.event}\n`
}
// ...
if (typeof message.id === 'string' || typeof message.id === 'number') {
  output += `id: ${message.id}\n`
}
```

The SSE specification treats `\r`, `\n`, and `\r\n` as line terminators. A `\n` (or `\r`) embedded in either field is rendered as the end of that field, allowing the rest of the input to be interpreted by the client as new SSE fields.

By contrast, `data` and `comment` already normalize all three line-terminator forms via `NEWLINES_RE = /(\r\n|\r|\n)/g`, so they are not affected.

### Proof of concept

```js
import {encode} from 'eventsource-encoder'

// Attacker-controlled value flows into `event`
const userSuppliedTopic = 'message\nevent: admin\ndata: {"role":"admin"}'

console.log(encode({event: userSuppliedTopic, data: 'hello'}))
```

Output:

```
event: message
event: admin
data: {"role":"admin"}
data: hello

```

The browser sees two events: a forged `admin` event with attacker-chosen payload, followed by the legitimate `message` event. The same primitive works through `id` for any string id value.

### Impact

If untrusted input is passed into the `event` or `id` field of a message, an attacker can:

- Spoof events of arbitrary type (rerouting payloads to handlers the attacker chooses)
- Inject additional SSE fields (`data:`, `id:`, `retry:`) into the stream
- Split a single `encode()` call into multiple distinct browser events
- Override the client's `Last-Event-ID` via injected `id:` lines

The vulnerability requires that an application places attacker-controlled data into `event` or `id`. Applications that only put trusted, statically-defined values into these fields are not affected.

### Patches

Fixed in `eventsource-encoder@1.0.2`. The `event` and string `id` fields are now validated; any value containing `\r` or `\n` causes the encoder to throw a `TypeError` rather than emit a malformed stream.

### Workarounds

If users cannot upgrade, validate or strip line terminators from any untrusted value before passing it to `encode` / `encodeMessage`:

```js
function safeSingleLine(value) {
  if (/[\r\n]/.test(value)) throw new Error('SSE field must be single-line')
  return value
}

encode({event: safeSingleLine(topic), id: safeSingleLine(id), data})
```

### Resources

- Related advisory (different package, same class): https://github.com/advisories/GHSA-4hxc-9384-m385
- SSE spec, line terminators: https://html.spec.whatwg.org/multipage/server-sent-events.html#parsing-an-event-stream

### Credit

Discovered while reviewing in light of GHSA-4hxc-9384-m385.

## References
- https://github.com/rexxars/eventsource-encoder/security/advisories/GHSA-m9g3-3g99-mhpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44214
- https://github.com/rexxars/eventsource-encoder
- https://html.spec.whatwg.org/multipage/server-sent-events.html#parsing-an-event-stream
