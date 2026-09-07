# [M] markdown-it: Quadratic complexity DoS in smartquotes rule via replaceAt string operations

## Summary
Severity: Medium
Advisory: GHSA-6v5v-wf23-fmfq
CVE: CVE-2026-48988
CWE: CWE-400, CWE-407
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-6v5v-wf23-fmfq
Type: github-advisory

## Affected
- npm: `markdown-it` — affected >=0 <14.2.0

## Details
### Summary

A quadratic time complexity vulnerability exists in markdown-it's smartquotes rule (enabled via the `typographer: true` option). An attacker can craft a markdown input consisting of consecutive quotation marks that causes the parser to consume excessive CPU time, leading to denial of service.

### Details

The vulnerability is in the `replaceAt()` helper function used by the smartquotes rule in `lib/rules_core/smartquotes.mjs`:

```javascript
function replaceAt (str, index, ch) {
  return str.slice(0, index) + ch + str.slice(index + 1)
}
```

When markdown-it processes a text token containing many quotation marks (either `"` or `'`) with `typographer: true`, the smartquotes rule iterates through each quote character and calls `replaceAt()` to substitute it with a typographic (curly) quote. Each call to `replaceAt()` creates three new string slices and concatenates them, which is an O(n) operation where n is the length of the string.

Since this is called once per quote character in the token, and there are n quote characters, the total time complexity becomes O(n^2).

The root cause is that the smartquotes rule modifies `token.content` in place using string slicing rather than building the result incrementally. The `process_inlines()` function (line 14) processes each quote in the text token, and for matching quote pairs, calls `replaceAt()` on both the opening and closing token's content (lines 151-152). When the entire input is a single text token of quote characters, this results in quadratic behavior.

### PoC

```javascript
const md = require('markdown-it');
const instance = md({ typographer: true });

// 160,000 consecutive double-quote characters
const payload = '"'.repeat(160000);

console.time('render');
instance.render(payload);
console.timeEnd('render');
// Output: render: ~21000ms (21 seconds)

// Compare with typographer disabled:
const safe = md({ typographer: false });
console.time('render-safe');
safe.render(payload);
console.timeEnd('render-safe');
// Output: render-safe: ~8ms
```

Measured timing on a modern system:
- 10,000 quotes: ~19ms
- 20,000 quotes: ~51ms
- 40,000 quotes: ~212ms
- 80,000 quotes: ~5,430ms
- 160,000 quotes: ~21,198ms

The scaling is clearly superlinear (quadratic), with the 80K->160K step showing a ~3.9x increase for a 2x input increase, consistent with O(n^2).

### Impact

Applications that render user-supplied markdown with `typographer: true` are vulnerable to denial of service. An attacker can submit a relatively small payload (160KB of quote characters) that causes the server to spend over 21 seconds processing a single request. Repeated submissions can exhaust server CPU resources and prevent legitimate users from being served.

The impact is mitigated by the fact that the `typographer` option defaults to `false` and must be explicitly enabled. However, the typographer feature is commonly enabled in production applications that want smart typography, and the markdown-it documentation prominently suggests enabling it.

A suggested fix would be to replace the `replaceAt()` approach with an array-based or StringBuilder-style approach that collects all replacements and applies them in a single pass, reducing the time complexity to O(n).

## References
- https://github.com/markdown-it/markdown-it/security/advisories/GHSA-6v5v-wf23-fmfq
- https://github.com/markdown-it/markdown-it
