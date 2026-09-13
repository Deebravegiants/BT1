# [H] brace-expansion: DoS via exponential-time expansion of consecutive non-expanding {} groups

## Summary
Severity: High
Advisory: GHSA-3jxr-9vmj-r5cp
CVE: CVE-2026-13149
CWE: CWE-400, CWE-407
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-3jxr-9vmj-r5cp
Type: github-advisory

## Affected
- npm: `brace-expansion` — affected >=3.0.0 <5.0.7
- npm: `brace-expansion` — affected >=0 <1.1.16
- npm: `brace-expansion` — affected >=2.0.0 <2.1.2

## Details
### Summary
brace-expansion's expand() exhibits exponential-time - O(2ⁿ) - behavior in the number of consecutive non-expanding {} groups. A short, all-ASCII input (~90 bytes/30 groups) blocks the calling thread for minutes; a slightly longer input hangs it effectively indefinitely. Because the dominant consumers run on Node's single-threaded event loop, one small input can fully stall a worker/process.

In `expand_`, `post` is computed unconditionally at the top of the function, before the early-return branches that don't use it:
```js
const post = m.post.length ? expand_(m.post, max, false) : [''];   // always recurses
  ...
if (!isSequence && !isOptions) {
  if (m.post.match(/,(?!,).*\}/)) {
    str = m.pre + '{' + m.body + escClose + m.post;
    return expand_(str, max, true); // restart — `post` discarded
  }
  return [str];
}
```

For input like a{},{},…, the first {} is non-expanding, so control reaches the {a},b} rewrite branch - but `expand_` has already recursed into post over the entire remaining tail, only to throw the result away.
Each level therefore spawns two recursive expansions over essentially the same remaining work: `T(n) = 2·T(n−1) ⇒ O(2ⁿ)`.

The max option does not mitigate this: max only bounds the output-building loops; neither the post recursion nor the rewrite recursion consults it.
  
Measured on 5.0.6:

| groups (n) | input bytes | time |
|---|---|---|
| 20 | 60 | 130 ms |
| 24 | 72 | 1.9 s |
| 26 | 78 | 7.8 s |
| 30 (PoC) | 90 | ~2 min |

### Proof of concept
```js
const { expand } = require('brace-expansion');
// 30 non-expanding groups, ~90 bytes — blocks for minutes:
expand('a{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}');
```

### Impact

Any application that passes attacker-influenced strings to brace-expansion.expand() - directly or transitively via minimatch/glob brace patterns - can be driven into a multi-minute-to-indefinite CPU hang by a tiny request, denying service on that thread/process.

### Remediation

Upgrade to a patched release. The fix:
1. Defers computing post until after the early-return branches (and computes it locally in the $-suffix branch), so post is only expanded when a brace set actually expands and the value is used. This alone removes the exponential.
1. Converts the {a},b} rewrite from recursion to an in-function loop, so a long run of rewrites cannot grow the call stack.

Verified: the PoC drops from ~2 min to 0.55 ms, 5,000 groups complete in ~344 ms, and output is identical to 5.0.6 across a behavioral-equivalence suite (sequences, padding, $-prefix, a{},b}c, {},a}b, x{{a,b}}y, etc.). Post-fix complexity is ~O(n²) on this input class - acceptable for the security fix; a linear rewrite can be a non-urgent follow-up.

If immediate upgrade isn't possible, avoid passing untrusted input to expand() / glob brace patterns, or run such expansion under a timeout/worker.

## References
- https://github.com/juliangruber/brace-expansion/security/advisories/GHSA-3jxr-9vmj-r5cp
- https://nvd.nist.gov/vuln/detail/CVE-2026-13149
- https://github.com/juliangruber/brace-expansion/pull/122
- https://github.com/juliangruber/brace-expansion/pull/123
- https://github.com/juliangruber/brace-expansion/commit/835d6be91201122d9adffb0c0c8c094189ace265
- https://github.com/juliangruber/brace-expansion/commit/c7e33ec13ac1a684c116720843ce24e208611754
- https://github.com/juliangruber/brace-expansion/commit/d74e63030c012e3b7ae81657b8d665619cd51b95
- https://github.com/juliangruber/brace-expansion
- https://github.com/juliangruber/brace-expansion/releases/tag/v1.1.16
- https://github.com/juliangruber/brace-expansion/releases/tag/v2.1.2
- https://github.com/juliangruber/brace-expansion/releases/tag/v5.0.7
- https://www.npmjs.com/package/brace-expansion
