# [H] vm2's bufferAllocLimit cap bypassed by Buffer.concat and Buffer.from arrayLike

## Summary
Severity: High
Advisory: GHSA-gmc2-2x9w-cgh9
CVE: CVE-2026-47683
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-gmc2-2x9w-cgh9
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.6

## Details
## Summary

vm2 bufferAllocLimit cap bypassed by Buffer.concat and Buffer.from arrayLike

The `bufferAllocLimit` option introduced in 3.11.0 (GHSA-6785-pvv7-mvg7) caps host-side Buffer allocations driven by sandbox code, the way embedders opt into `timeout`. The cap wraps `Buffer.alloc`, `Buffer.allocUnsafe`, `Buffer.allocUnsafeSlow`, and the deprecated `Buffer(N)` / `new Buffer(N)` forms. Two other API paths reach the same host C++ allocator with an attacker-controlled size and are not capped: `Buffer.concat(list, totalLength)` and `Buffer.from(arrayLike)` with a fake `length`. Sandbox code can use either to allocate an arbitrary number of host external bytes in a single call, defeating the explicit DoS mitigation the embedder configured.

## Details

`lib/setup-sandbox.js` installs `checkBufferAllocLimit` at every wrapped entry to host Buffer allocation:

- `alloc()` at `lib/setup-sandbox.js:474` and the `connect(alloc, host.Buffer.alloc)` at line 480.
- `allocUnsafe()` at line 488 and `connect(allocUnsafe, host.Buffer.allocUnsafe)` at line 496.
- `allocUnsafeSlow()` at line 504 and `connect(allocUnsafeSlow, host.Buffer.allocUnsafeSlow)` at line 510.
- `BufferHandler.apply` at line 424 and `BufferHandler.construct` at line 433 for the deprecated `Buffer(N)` / `new Buffer(N)` numeric-first-arg paths.

`Buffer.concat` is not wrapped. The sandbox-visible `Buffer.concat` is therefore the bridge proxy of the host `Buffer.concat`, which calls into Node's `Buffer.allocUnsafe(totalLength)` internally without going through the sandbox-side `allocUnsafe` wrapper. Same for `Buffer.from` when the argument is array-like (`{length: N}`): Node's `fromArrayLike` allocates a buffer of size `N` before the iteration that fills it. Neither of those allocator paths consult `localBufferAllocLimit`.

The mitigation rationale documented in `docs/ATTACKS.md` Category 23 explicitly enumerates the surfaces that were considered and either capped (Buffer.alloc family) or punted to follow-up (`new Uint8Array(N)`, `new ArrayBuffer(N)`, `String.prototype.repeat`). `Buffer.concat(list, totalLength)` is not listed in either group, and `Buffer.from(arrayLike)` is mentioned only as "bounded by source array size which had to be allocated through some other path first" -- which is not true for the `{length: N}` form, because no array of length `N` actually exists.

A single call from sandbox to `Buffer.concat([Buffer.from('a')], 50 * 1024 * 1024)` allocates 50 MiB of host external memory. The allocation itself is a single synchronous host C++ call that `timeout` cannot interrupt, exactly like the original advisory. The zero-fill that follows is interruptible, but the memory is already committed by the time the interrupt could fire, so the embedder's container memory budget is the only ceiling. The same pattern in a loop, or with a larger `totalLength`, drives RSS up by hundreds of megabytes per call.

The fix uses the existing `checkBufferAllocLimit(size)` helper and a sandbox-side wrapper installed via `connect(...)` -- one for `Buffer.concat` that sums the `totalLength` (or falls back to summing list lengths) and one for `Buffer.from` that recognises the array-like-with-numeric-`length` branch.

## PoC

```javascript
'use strict';
const { VM, NodeVM } = require('vm2');

function ext() { return Math.round(process.memoryUsage().external / 1024 / 1024); }
function tryBypass(label, code) {
    const ext0 = ext();
    let buf;
    try { buf = code(); }
    catch (e) {
        console.log(`[${label}] CAPPED -- ${String(e).split('\n')[0]}`);
        return;
    }
    console.log(`[${label}] BYPASSED -- got ${buf && buf.length} bytes (external +${ext() - ext0} MB)`);
}

console.log('Cap is configured at 1024 bytes.\n');

const vm1 = new VM({ bufferAllocLimit: 1024 });
tryBypass('VM Buffer.alloc(50MB)        ',
    () => vm1.run('Buffer.alloc(50 * 1024 * 1024)'));

const vm2 = new VM({ bufferAllocLimit: 1024 });
tryBypass('VM Buffer.concat 50MB        ',
    () => vm2.run('Buffer.concat([Buffer.from("a")], 50 * 1024 * 1024)'));

const vm3 = new NodeVM({ bufferAllocLimit: 1024 });
tryBypass('NodeVM Buffer.concat 50MB    ',
    () => vm3.run('module.exports = Buffer.concat([Buffer.from("a")], 50 * 1024 * 1024);'));

const vm4 = new VM({ bufferAllocLimit: 1024 });
tryBypass('VM Buffer.from({length: 8MB})',
    () => vm4.run('Buffer.from({length: 8 * 1024 * 1024})'));
```

Run with `node poc.js` against `vm2@3.11.3`:

```
Cap is configured at 1024 bytes.

[VM Buffer.alloc(50MB)        ] CAPPED -- RangeError: Buffer allocation size 52428800 exceeds bufferAllocLimit 1024
[VM Buffer.concat 50MB        ] BYPASSED -- got 52428800 bytes (external +50 MB)
[NodeVM Buffer.concat 50MB    ] BYPASSED -- got 52428800 bytes (external +50 MB)
[VM Buffer.from({length: 8MB})] BYPASSED -- got 8388608 bytes (external +8 MB)
```

Process RSS climbs by the same amount each call, confirming a real host C++ allocation rather than a sandbox-realm-only effect.

## Impact

This is the same DoS class GHSA-6785-pvv7-mvg7 was filed for: untrusted sandbox code amplifying a small payload into a large synchronous host external-memory allocation that V8's `timeout` cannot preempt. In the environments the advisory cites -- Docker memory limits, Kubernetes pods, AWS Lambda -- a single 200-byte sandbox payload can drive a multi-hundred-megabyte RSS jump and OOM the host process.

The Category 23 fix was specifically scoped to "cap host Buffer external allocation" and embedders are documented to opt into `bufferAllocLimit` as their layered defense against this class. The two paths above are uncapped, so an embedder that has configured `bufferAllocLimit: 32 * 1024 * 1024` (the value recommended in the README's Hardening recommendations) is still vulnerable to the exact attack the option was designed to prevent. The mitigation invariant -- "every Buffer external allocation driven by sandbox code is capped by `bufferAllocLimit`" -- does not hold.

No sandbox escape; pure DoS.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-gmc2-2x9w-cgh9
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/3.11.6
