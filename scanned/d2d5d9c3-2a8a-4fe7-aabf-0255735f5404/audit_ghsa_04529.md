# [H] Deno: Miller-Rabin Primality Test Allows Zero Rounds

## Summary
Severity: High
Advisory: GHSA-9xg4-qhm4-g43w
CVE: CVE-2026-49440
CWE: CWE-325
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-9xg4-qhm4-g43w
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.8.1

## Details
## Summary

`node:crypto.checkPrime(candidate[, options][, callback])` and `crypto.checkPrimeSync(candidate[, options])` ran no Miller-Rabin rounds at all when the caller left `options.checks` at its default of `0`. In that mode, the only test applied to the candidate was trial division by the primes up to `17,863`. Any composite whose smallest prime factor exceeds that bound — for example the product of two primes just above it, such as `17,881 × 17,891` — was reported as `true` ("probably prime").

The same divergence affected the lower-level `op_node_check_prime` / `op_node_check_prime_bytes` paths that the polyfill calls into.

Node.js itself does not have this problem: it forwards `checks = 0` to OpenSSL's `BN_check_prime`, which substitutes a sensible default number of rounds based on the candidate's bit length (per FIPS 186-4 Appendix C.3 Table C.1). Deno's Rust implementation had no equivalent fallback, so `count = 0` meant "skip the loop entirely."

## Affected APIs

- `crypto.checkPrime(candidate)` (callback form, default options)
- `crypto.checkPrime(candidate, { checks: 0 }, callback)`
- `crypto.checkPrimeSync(candidate)` (default options)
- `crypto.checkPrimeSync(candidate, { checks: 0 })`

Callers who explicitly passed `checks >= 1` were less affected, the loop ran the number of rounds they asked for, but were still receiving fewer rounds than Node would have applied for the same bit length. With the patched version they get at least the FIPS minimum.

## Not affected

- Deno's prime *generation* (`crypto.generatePrime`, `crypto.generatePrimeSync`, and the DH parameter generation path). Those routes go through `Prime::generate_with_options` in `ext/node_crypto/primes.rs`, which hardcodes `20` Miller-Rabin rounds and never reads a user-controlled `checks` value, so the bug never reached them.
- Any other Deno-internal use of primality testing — `is_probably_prime` is not called from elsewhere in the runtime with `count = 0`. 
- Web Crypto (`crypto.subtle.*`), which uses entirely separate code paths and does not expose a primality test.

## Impact

The realistic exposure is application-level: a Deno program that calls `crypto.checkPrime` (or its sync variant) with default options to validate an externally-supplied bignum, for example checking a peer-provided Diffie-Hellman prime, validating a prime read from configuration, or sanity-checking an RSA factor, will accept crafted composites as prime. The composite is trivial to construct: any product of two primes greater than `17,863` works.

Downstream consequences depend on what the program does with the "verified" prime. If the prime is fed into a key exchange, signature verification, or factorization-style check, the security guarantees of that protocol collapse to whatever the attacker engineered into the composite.

The CVSS impact is bounded by the requirement that the victim application both (a) calls `checkPrime` with default options and (b) acts on the result for security-relevant input it does not control.

## Reproduction

```ts
import { checkPrimeSync } from "node:crypto";

// 17881 and 17891 are both prime and both above the trial-division
// ceiling used by Deno's implementation.
const composite = 17881n * 17891n;

// Affected versions print `true`; the patched version prints `false`.
console.log(checkPrimeSync(composite));
```

The same result is reproducible from Rust against the internal helper:

```rust
use num_bigint::BigInt;
let composite = BigInt::from(17881u32) * BigInt::from(17891u32);
assert!(!is_probably_prime(&composite, 0)); // fails on affected versions
```

## Fix

PR [#34391](https://github.com/denoland/deno/pull/34391) introduces a
helper `min_miller_rabin_rounds_for_bits(bits)` that returns the FIPS
186-4 Appendix C.3 round counts, matching the defaults OpenSSL uses
inside `BN_check_prime`. `is_probably_prime` then clamps the loop bound
to `count.max(min_miller_rabin_rounds_for_bits(n.bits()))`. The
probabilistic loop now always executes, regardless of what `checks`
value the caller supplied, with a round count strong enough to keep the
false-positive probability below 2^-80. Callers that pass a larger
explicit `checks` still get exactly that many rounds.

Unit tests under `ext/node_crypto/primes.rs` cover the
`17,881 × 17,891` case, a larger 64-bit composite, and the FIPS lookup
table itself.

## Workarounds

If you cannot upgrade immediately:

- **Pass an explicit `checks` value** when calling `crypto.checkPrime` or `crypto.checkPrimeSync`. A value of `64` is conservative for any reasonable bit length and keeps the loop running.
- **Do not rely on `crypto.checkPrime` to validate attacker-influenced bignums** in security-critical paths until you are on the patched release.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-9xg4-qhm4-g43w
- https://github.com/denoland/deno/pull/34391
- https://github.com/denoland/deno
