# [H] linkify-it: Quadratic-complexity DoS via the `mailto:` validator scan-loop on attacker text

## Summary
Severity: High
Advisory: GHSA-v245-v573-v5vm
CVE: CVE-2026-59887
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-v245-v573-v5vm
Type: github-advisory

## Affected
- npm: `linkify-it` — affected >=0 <5.0.2

## Details
### Summary
`linkify-it`'s schema-scan loop (`.test()` / `.match()`, the documented public API) invokes the `mailto:`
schema validator at **every** `mailto:` occurrence in the input text. For each occurrence the validator does
`text.slice(pos)` (an O(n) copy) and runs an email regex whose local-part class `src_email_name` greedily
scans the **entire remaining tail** (O(n)) before failing. With N `mailto:` occurrences that is
**N × O(n) = O(n²)**. Because linkify-it runs on arbitrary user text (markdown-it feeds it whole documents
when `linkify:true`), an unauthenticated attacker can block the single-threaded event loop for many seconds
with a small input. No length bound (unlike an HTTP header).

### Root cause — `index.mjs` + `lib/re.mjs`
```js
// index.mjs (mailto validator) — runs at every "mailto:" hit
'mailto:': { validate: function (text, pos, self) {
  const tail = text.slice(pos)                                  // O(n) copy per hit
  if (!self.re.mailto) self.re.mailto = new RegExp('^' + self.re.src_email_name + '@' + self.re.src_host_strict, 'i')
  if (self.re.mailto.test(tail)) { ... }                        // scans the whole O(n) tail
  return 0
}}
// lib/re.mjs:91-93 — every char of "mailto:" (incl. ':','-',';') is in this class:
re.src_email_name = '[\\-;:&=\\+\\$,\\.a-zA-Z0-9_][\\-;:&=\\+\\$,\\"\\.a-zA-Z0-9_]*'
```
The `while ((m = re.exec(text)) !== null) { …testSchemaAt… }` scan loop calls the validator at each
`mailto:` hit; `src_email_name` greedily consumes the whole tail (all chars are in its class) then fails for
lack of `@`. `http:`/`https:` do NOT blow up — their validator requires the tail to start with `//`, failing
in O(1) per hit.

### Proof of Concept (confirmed, linkify-it 5.0.1, Node v24)
```js
const LinkifyIt = require('linkify-it');
const lf = new LinkifyIt();
lf.match('mailto:'.repeat(48000));   // ~336 KB of "mailto:mailto:…" -> seconds of blocked event loop
```
| input (same bytes) | 56 KB | 112 KB | 224 KB | 336 KB |
|---|---:|---:|---:|---:|
| **`mailto:` contiguous** | 97 ms | 357 ms | 1438 ms | 3272 ms |
| `mailto:` space-separated | 2 ms | 3 ms | 5 ms | 8 ms |
| `http://` contiguous | 12 ms | 17 ms | 33 ms | 49 ms |

×~4 per 2× input ⇒ O(n²); equal-byte controls stay flat ⇒ algorithmic, not a GC/allocation artifact.
Real-world via markdown-it 14.x (`{linkify:true}`), `md.render('mailto:'.repeat(n))`: 219 KB ≈ ~5 s.
<img width="737" height="161" alt="image" src="https://github.com/user-attachments/assets/b5d390f3-68d0-4861-9c47-ad8aff0203d5" />

### Impact
Reachable on arbitrary user text via the documented `.test()`/`.match()` API and through markdown-it's
linkifier — comment systems, chat, forums, wikis, note apps that render user markdown with linkify enabled.
A ~220 KB post hangs the event loop ~5 s; a few hundred KB → tens of seconds. Availability only.

### Suggested remediation
Bound the email local-part per RFC 5321 (≤64) so per-hit work is O(1), and avoid the full-tail slice:
```js
// lib/re.mjs — cap the greedy run:
re.src_email_name = '[\\-;:&=\\+\\$,\\.a-zA-Z0-9_][\\-;:&=\\+\\$,\\"\\.a-zA-Z0-9_]{0,63}'
// index.mjs — prefer a sticky regex anchored at `pos` over text.slice(pos).
```

### Affected / disclosure
All versions through 5.0.1 (latest); same code on `master`. cve-mcp/OSV report no known vulnerability for
linkify-it. Distinct from markdown-it's own `*`-run ReDoS (CVE-2026-2327, different package/path) and the
recent markdown-it DoS. Reported privately; happy to test a patch against the PoC.

## References
- https://github.com/markdown-it/linkify-it/security/advisories/GHSA-v245-v573-v5vm
- https://nvd.nist.gov/vuln/detail/CVE-2026-59887
- https://github.com/markdown-it/linkify-it/commit/105e5d77f7d119871d2b2d86ed208568eb3e7ffe
- https://github.com/markdown-it/linkify-it
- https://github.com/markdown-it/linkify-it/releases/tag/5.0.2
