### Title
Unbounded gzip decompression in `unzipIcon` allows memory-exhaustion DoS via malicious token icon - ([File: adapters/storage-icons-mobile/src/icons-storage.js])

### Summary
`storeIcons` → `#storeIcon` → `unzipIcon` calls `pako.ungzip(arr, { to: 'string' })` on attacker-controlled base64 gzip data with no pre-decompression size cap, meaning `cleanupSVG`/`validateSVG` (which do enforce some content shape/length rules) only run *after* the full decompressed string is already materialized in memory. A small malicious gzip payload with a very high compression ratio can force a huge in-memory string allocation on the device before any validation occurs.

### Finding Description
The relevant code: [1](#0-0) 

`unzipIcon` takes `token.icon` (base64), decodes it into a `Uint8Array`, and immediately calls `ungzip(arr, { to: 'string' })` with no limit on `arr` length or on the resulting decompressed string size. Only after decompression does it call `cleanupSVG`, which in turn calls `validateSVG`: [2](#0-1) 

`validate.mjs` does perform structural checks (tag whitelist, per-attribute regex, a 50,000-char cap on `<path d="...">` values) but these all operate on the string *after* it has already been fully decompressed and is resident in memory: [3](#0-2) 

This is called from `storeIcons`, which is reachable from `#storeIcon` for any token where `token.icon` is truthy: [4](#0-3) 

Since `storeIcons` is invoked from the assets feature (`features/assets-feature/module/assets-module.js`) as part of ingesting token/asset metadata (e.g., custom token lists), and there is no size limit imposed on the base64 input nor on the decompressed output before `ungzip` runs, an attacker who controls a token's `icon` field (a "zip bomb": a small, highly-compressible gzip stream) can force the app to allocate an arbitrarily large string in memory. This can exhaust available memory/degrade the device before `validateSVG`'s length checks or tag whitelist ever get a chance to reject the content.

### Impact Explanation
This is a device-level availability issue: a single malicious token icon in a fetched or imported token list can cause pako to attempt to allocate an oversized string (limited only by gzip's max compression ratio and JS engine string/array limits), leading to out-of-memory crashes or severe slowdown of the wallet app/process. This does not lead to key disclosure or signing bypass, but it degrades availability of a process that also handles wallet unlock/signing, matching a scoped "availability/DoS" impact rather than a critical fund-loss impact.

### Likelihood Explanation
Feasible and repeatable: any flow that calls `storeIcons` with attacker/third‑party-controlled `token.icon` values (e.g., ingesting a custom/third-party token list, which the code explicitly supports via `#customTokensIconsEnabled`) reaches `unzipIcon` directly with no upstream size gating. A gzip "bomb" (e.g., a highly repetitive small payload) is trivial to construct, and the exploit requires no privileged state, keys, or user interaction beyond the app processing the token list — this matches an unprivileged remote-content-injection scenario.

### Recommendation
Enforce limits before and during decompression in `unzipIcon`:
- Cap the input base64/compressed length before attempting to decompress.
- Use a streaming ungzip (or manually chunked decompression) with a hard maximum output size, aborting/throwing once a reasonable SVG icon size threshold (e.g., a few hundred KB) is exceeded, rather than allowing `pako.ungzip` to fully materialize an unbounded string first.
- Only pass the decompressed data to `cleanupSVG`/`validateSVG` once the size cap has been enforced.

### Proof of Concept
Unit test plan for `adapters/storage-icons-mobile/src/icons-storage.js`:
1. Construct a gzip payload with a very high compression ratio (e.g., gzip of a string consisting of millions of repeated characters, compressing down to a few KB).
2. Base64-encode it and call `unzipIcon(base64)` (or `storeIcons([{ name: 'test', icon: base64 }])`).
3. Assert that the function throws or rejects due to an enforced size limit *before* the fully decompressed string is created/returned, e.g. `expect(() => unzipIcon(bombBase64)).toThrow(/size limit/)`.
4. Currently, no such assertion can pass because no length cap exists prior to `ungzip`/`cleanupSVG`, demonstrating the gap — decompression proceeds fully and only the unrelated tag/attribute/path-length validation in `validate.mjs` might incidentally reject content afterward (too late to prevent the memory spike).

### Citations

**File:** adapters/storage-icons-mobile/src/icons-storage.js (L26-56)
```javascript
  storeIcons = async (tokens) => {
    if (!this.#customTokensIconsEnabled) return

    await this.#ensureIconsDir()

    return Promise.all(
      tokens.map(async (token) => {
        if (token.icon) {
          await this.#storeIcon(token)
        } else if (isNull(token.icon)) {
          await this.#deleteIcon(token)
        }
      })
    )
  }

  getIcon = async (assetName) => {
    const path = this.#getPath(assetName)
    const fileExists = await RNFS.exists(path)
    if (!fileExists) return null
    const data = await RNFS.readFile(path, 'utf8')
    validateSVG(data)
    return data
  }

  #storeIcon = async (token) => {
    const assetName = token.name || token.assetName
    const path = this.#getPath(assetName)
    const svg = await unzipIcon(token.icon)
    await RNFS.writeFile(path, svg, 'utf8')
  }
```

**File:** adapters/storage-icons-mobile/src/icons-storage.js (L80-86)
```javascript
const unzipIcon = (base64) => {
  const buff = Buffer.from(base64, 'base64')
  const arr = Uint8Array.from(buff)
  const data = ungzip(arr, { to: 'string' })
  const str = data.toString('utf8')
  return cleanupSVG(str)
}
```

**File:** libraries/svg-safe/src/cleanup.mjs (L1-10)
```javascript
import { validate } from './validate.mjs'

export function cleanup(svg) {
  const clean = svg
    .replace(/<!--[^>]+-->/gu, '')
    .replace(/<title>[^>]+<\/title>/gu, '')
    .replace(/\s+/gu, ' ')
  validate(clean)
  return clean
}
```

**File:** libraries/svg-safe/src/validate.mjs (L237-247)
```javascript
export function validate(raw) {
  assert(typeof raw === 'string', `validate: raw is not a string`)
  assert(!/['`]/u.test(raw), `validate: "${raw}" is not valid`) // just an extra check
  for (const token of tokenizeFile(raw)) {
    if (token.trim() === '') continue
    const [tag, ...options] = tokenizeLine(token)
    assert(allTags.has(tag), `validate: invalid tag "${tag}"`)
    if (tag.startsWith('/')) assert(options.length === 0, `validate: "${tag}" starts with /`)
    for (const option of options) validateOption(tag, option.replace(/^ +/u, ''))
  }
}
```
