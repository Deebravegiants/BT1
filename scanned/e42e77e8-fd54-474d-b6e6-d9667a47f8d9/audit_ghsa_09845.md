# [M] LiquidJS: `renderFile()` / `parseFile()` bypass configured `root` and allow arbitrary file read

## Summary
Severity: Medium
Advisory: GHSA-v273-448j-v4qj
CVE: CVE-2026-39859
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-v273-448j-v4qj
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0 <10.25.5

## Details
`liquidjs` 10.25.0 documents `root` as constraining filenames passed to `renderFile()` and `parseFile()`, but top-level file loads do not enforce that boundary.

The published npm package `liquidjs@10.25.0` on Linux 6.17.0 with Node v22.22.1. A `Liquid` instance configured with an empty temporary directory as `root` still returned the contents of `/etc/hosts` when `renderFile('/etc/hosts')` was called. I have not exhaustively checked older releases yet; 10.25.0 is the latest tested version.

Root cause:
- `src/parser/parser.ts:83-85` calls `loader.lookup(file, LookupType.Root, ...)` and then reads the returned file.
- `src/fs/loader.ts:38` passes `type !== LookupType.Root` into `candidates()`.
- For `LookupType.Root`, `enforceRoot` is false, so `src/fs/loader.ts:47-66` accepts resolved absolute paths and fallback results without any `contains()` check.

This appears adjacent to the March 10, 2026 fix for CVE-2026-30952, which hardened `include` / `render` / `layout` but not the top-level file-loading APIs.

Proof of concept:
```javascript
const fs = require('fs');
const os = require('os');
const path = require('path');
const { Liquid } = require('liquidjs');

const safeRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'liquidjs-safe-root-'));
const engine = new Liquid({ root: [safeRoot], extname: '.liquid' });

engine.renderFile('/etc/hosts').then(console.log);
```

Expected result: a path outside `root` should be rejected.
Actual result: `/etc/hosts` is rendered successfully.

Impact: any application that treats `root` as a sandbox boundary and forwards attacker-controlled template names into `renderFile()` or `parseFile()` can disclose arbitrary local files readable by the server process.

Suggested fix: apply the same containment checks used for partial/layout lookups to `LookupType.Root`, and reject absolute or fallback paths unless they remain within an allowed root. A regression test should verify that `renderFile('/etc/hosts')` fails when `root` points to an unrelated directory.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-v273-448j-v4qj
- https://nvd.nist.gov/vuln/detail/CVE-2026-39859
- https://github.com/harttle/liquidjs/pull/870
- https://github.com/harttle/liquidjs/commit/f41c1fc02fe901598f3328118b42b13bc6bc9b04
- https://github.com/harttle/liquidjs
- https://github.com/harttle/liquidjs/releases/tag/v10.25.5
