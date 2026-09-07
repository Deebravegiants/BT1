# [H] js-yaml: Exponential parsing time in flow collections leads to denial of service

## Summary
Severity: High
Advisory: GHSA-pm4m-ph32-ghv5
CVE: CVE-2026-73643
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-pm4m-ph32-ghv5
Type: github-advisory

## Affected
- npm: `js-yaml` — affected >=5.0.0 <5.2.2

## Details
### Summary
Parsing a small YAML document can take exponential time. An application that calls `load()` or `loadAll()` on untrusted input can be hung by a payload under 200 bytes.

### Details
When an entry in a flow sequence turns out to be a `key: value` pair, the parser rewinds and parses that entry a second time as the key.
If the key is itself a nested flow sequence of the same shape, every level is parsed twice, so the total work is O(2^n) in the nesting depth. The default `maxDepth` of 100 does not help, because the time is already unmanageable at about 30 to 40 levels.

Root cause, potentially the: `readFlowCollection` in [parser.ts](https://github.com/nodeca/js-yaml/blob/master/src/parser/parser.ts), the `restoreState` followed by a second `parseNode` further down.


### PoC

```javascript
const yaml = require('js-yaml')
const n = 30
yaml.load('[ '.repeat(n) + '1' + ' ]: 0'.repeat(n))
```

With default options: 22 levels takes about 1 second, 26 levels about 17 seconds, 30 levels over 2 minutes. The input stays under 200 bytes and grows linearly with `n`.

### Impact
Denial of service. A single small request can keep one CPU busy for minutes or longer and blocks the Node event loop, so one request can stall the whole process. No anchors, aliases, merges, tags, or non default options are required, and it reproduces on the default schema.

## References
- https://github.com/nodeca/js-yaml/security/advisories/GHSA-pm4m-ph32-ghv5
- https://github.com/nodeca/js-yaml/commit/3e5240f9cbe645ce5afb58524954a13c8539c853
- https://github.com/nodeca/js-yaml
- https://github.com/nodeca/js-yaml/releases/tag/5.2.2
