# [H] Boa has an uncaught exception when transitioning the state of `AsyncGenerator` objects

## Summary
Severity: High
Advisory: GHSA-f67q-wr6w-23jq
CVE: CVE-2024-43367
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-f67q-wr6w-23jq
Type: github-advisory

## Affected
- crates.io: `boa_engine` — affected >=0.16 <0.19.0

## Details
A wrong assumption made when handling ECMAScript's `AsyncGenerator` operations can cause an uncaught exception on certain scripts.

## Details

Boa's implementation of `AsyncGenerator` makes the assumption that the state of an `AsyncGenerator` object cannot change while resolving a promise created by methods of `AsyncGenerator` such as `%AsyncGeneratorPrototype%.next`, `%AsyncGeneratorPrototype%.return`, or `%AsyncGeneratorPrototype%.throw`.
However, a carefully constructed code could trigger a state transition from a getter method for the promise's `then` property, which causes the engine to fail an assertion of this assumption, causing an uncaught exception. This could be used to create a Denial Of Service attack in applications that run arbitrary ECMAScript code provided by an external user.

## Patches

Version 0.19.0 is patched to correctly handle this case.

## Workarounds

Users unable to upgrade to the patched version would want to use [`std::panic::catch_unwind`](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html) to ensure any exceptions caused by the engine don't impact the availability of the main application.

## References

- https://github.com/boa-dev/boa/commit/69ea2f52ed976934bff588d6b566bae01be313f7
- https://github.com/tc39/ecma262/security/advisories/GHSA-g38c-wh3c-5h9r

## References
- https://github.com/boa-dev/boa/security/advisories/GHSA-f67q-wr6w-23jq
- https://github.com/tc39/ecma262/security/advisories/GHSA-g38c-wh3c-5h9r
- https://nvd.nist.gov/vuln/detail/CVE-2024-43367
- https://github.com/boa-dev/boa/commit/69ea2f52ed976934bff588d6b566bae01be313f7
- https://github.com/boa-dev/boa
- https://rustsec.org/advisories/RUSTSEC-2024-0444.html
