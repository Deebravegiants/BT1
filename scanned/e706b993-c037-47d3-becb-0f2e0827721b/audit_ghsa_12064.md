# [M] brace-expansion: Zero-step sequence causes process hang and memory exhaustion

## Summary
Severity: Medium
Advisory: GHSA-f886-m6hf-6m8v
CVE: CVE-2026-33750
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-f886-m6hf-6m8v
Type: github-advisory

## Affected
- npm: `brace-expansion` — affected >=4.0.0 <5.0.5
- npm: `brace-expansion` — affected >=3.0.0 <3.0.2
- npm: `brace-expansion` — affected >=2.0.0 <2.0.3
- npm: `brace-expansion` — affected >=0 <1.1.13

## Details
### Impact

A brace pattern with a zero step value (e.g., `{1..2..0}`) causes the sequence generation loop to run indefinitely, making the process hang for seconds and allocate heaps of memory.

The loop in question:

https://github.com/juliangruber/brace-expansion/blob/daa71bcb4a30a2df9bcb7f7b8daaf2ab30e5794a/src/index.ts#L184

`test()` is one of

https://github.com/juliangruber/brace-expansion/blob/daa71bcb4a30a2df9bcb7f7b8daaf2ab30e5794a/src/index.ts#L107-L113

The increment is computed as `Math.abs(0) = 0`, so the loop variable never advances. On a test machine, the process hangs for about 3.5 seconds and allocates roughly 1.9 GB of memory before throwing a `RangeError`. Setting max to any value has no effect because the limit is only checked at the output combination step, not during sequence generation.

This affects any application that passes untrusted strings to expand(), or by error sets a step value of `0`. That includes tools built on minimatch/glob that resolve patterns from CLI arguments or config files. The input needed is just 10 bytes.

### Patches


Upgrade to versions
- 5.0.5+

A step increment of 0 is now sanitized to 1, which matches bash behavior.

### Workarounds

Sanitize strings passed to `expand()` to ensure a step value of `0` is not used.

## References
- https://github.com/juliangruber/brace-expansion/security/advisories/GHSA-f886-m6hf-6m8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33750
- https://github.com/juliangruber/brace-expansion/issues/98
- https://github.com/juliangruber/brace-expansion/pull/95
- https://github.com/juliangruber/brace-expansion/pull/96
- https://github.com/juliangruber/brace-expansion/pull/97
- https://github.com/juliangruber/brace-expansion/commit/311ac0d54994158c0a384e286a7d6cbb17ee8ed5
- https://github.com/juliangruber/brace-expansion/commit/7fd684f89fdde3549563d0a6522226a9189472a2
- https://github.com/juliangruber/brace-expansion/commit/b9cacd9e55e7a1fa588fe4b7bb1159d52f1d902a
- https://github.com/juliangruber/brace-expansion
- https://github.com/juliangruber/brace-expansion/blob/daa71bcb4a30a2df9bcb7f7b8daaf2ab30e5794a/src/index.ts#L107-L113
- https://github.com/juliangruber/brace-expansion/blob/daa71bcb4a30a2df9bcb7f7b8daaf2ab30e5794a/src/index.ts#L184
