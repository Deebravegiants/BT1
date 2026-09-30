# [H] PostCSS: Path Traversal in Previous Source Map Auto-Loading (sourceMappingURL) leads to Arbitrary .map File Disclosure

## Summary
Severity: High
Advisory: GHSA-r28c-9q8g-f849
CVE: CVE-2026-73646
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-r28c-9q8g-f849
Type: github-advisory

## Affected
- npm: `postcss` — affected >=0 <8.5.18

## Details
## Vulnerability Details

**File**: `lib/previous-map.js`
**Line**: 87-98 (`loadFile`), 129-144 (`loadMap`)


### Root Cause
PostCSS auto-detects a `/*# sourceMappingURL=... */` comment inside the CSS text it is asked to parse and, unless the caller explicitly passes `map: false`, attempts to load that path from disk as a "previous source map." This happens on every `postcss.parse()` / `postcss().process()` call by default (opt-out, not opt-in).

`loadMap()` builds the candidate path via `join(dirname(opts.from), annotation)`, where `annotation` is the raw, attacker-controlled string from the CSS comment. `path.join()` normalizes but does not sandbox `..` segments, so a `../../../` prefix walks the resolved path outside the intended directory. If `opts.from` is not set at all, the annotation is used completely unmodified — an absolute path in the CSS comment is read verbatim.

8.5.12 already fixed a strictly worse variant of this (any file, any extension, could be read) by requiring the resolved path to end in `.map` (`loadFile()`). That fix did not address the traversal itself, only the target extension. Since the `join(dirname(file), map)` logic has existed unchanged since PostCSS 8.0.0 (Feb 2020), any file ending in `.map` remains readable through this path in the current release (8.5.16).

Once loaded, `MapGenerator.isMap()` treats the mere presence of a loaded "previous map" as an implicit request to generate `result.map`, even when the caller never set the `map` option. If the loaded map has a `sourcesContent` field (common for maps emitted by bundlers/transpilers), that content is merged into `result.map` and returned to the caller — disclosing the traversed-to file's content to whoever supplied the CSS.

### Attack Scenario
1. A service accepts user-submitted CSS and runs it through PostCSS to lint/format/transform it, e.g. `postcss().process(userCss, { from: '/app/uploads/user123/input.css', to: '/app/uploads/user123/output.css' })` — idiomatic usage; `map` option untouched.
2. Attacker submits CSS containing `/*# sourceMappingURL=../../../../some/other/app/dist/bundle.js.map */` (or an absolute path if `from` is unset).
3. PostCSS reads that `.map` file and folds its `sourcesContent` into `result.map`.
4. The service does what most build pipelines do with a truthy `result.map` — writes it next to the CSS output or returns it via API (source maps are meant to be consumed by browser devtools, so this is commonly public/served).
5. Attacker retrieves the emitted map and reads out the traversed file's content.

### Impact
Disclosure of the contents of arbitrary `.map` files reachable via path traversal (or absolute path when `from` is unset) from the process's filesystem. Affects any application processing CSS it does not fully trust without explicitly passing `map: false`. No authentication or user interaction beyond submitting CSS text is required.

### Vulnerable Code
```js
loadFile(path, cssFile, trusted) {
  if (!trusted && !this.unsafeMap) {
    if (!/\.map$/i.test(path)) {
      return undefined
    }
  }
  this.root = dirname(path)
  if (existsSync(path)) {
    this.mapFile = path
    return readFileSync(path, 'utf-8').toString().trim()
  }
}

loadMap(file, prev) {
  ...
  } else if (this.annotation) {
    let map = this.annotation
    if (file) map = join(dirname(file), map)
    let unknown = this.loadFile(map, file, false)
    ...
  }
}
```

### Recommended Fix
Constrain the resolved path to remain inside the CSS file's own directory instead of relying solely on a filename-extension check:
```js
loadFile(path, cssFile, trusted) {
  if (!trusted && !this.unsafeMap) {
    if (!/\.map$/i.test(path)) {
      return undefined
    }
    if (!cssFile) return undefined
    let root = resolve(dirname(cssFile))
    let resolvedPath = resolve(root, path)
    if (resolvedPath !== root && !resolvedPath.startsWith(root + sep)) {
      return undefined
    }
  }
  this.root = dirname(path)
  if (existsSync(path)) {
    this.mapFile = path
    return readFileSync(path, 'utf-8').toString().trim()
  }
}
```
I've implemented, tested (full existing test suite — 660/660 passing, plus new PoC-based regression checks for both the traversal and legitimate same-directory cases), and can share this fix on request or via a private fork if invited.

### Verification
Dynamically confirmed on v8.5.16 (current npm release / repo HEAD) via a standalone Node.js harness against `lib/postcss.js`: a "secret" `.map` file placed two directories outside a simulated project directory was read via a crafted `sourceMappingURL` comment in otherwise-innocuous CSS, with its `sourcesContent` appearing verbatim in `result.map.toString()` — with no `map` option set by the caller. A second harness confirmed the simpler no-`from` case reads an absolute path directly. A third harness confirmed `map: false` is the only current workaround. The attached fix branch closes both vectors while keeping all 660 existing unit tests green.

## References
- https://github.com/postcss/postcss/security/advisories/GHSA-r28c-9q8g-f849
- https://github.com/postcss/postcss/commit/95663d3eb7ba26f4854dd19d3b4f4425760cf56c
- https://github.com/postcss/postcss
- https://github.com/postcss/postcss/releases/tag/8.5.18
