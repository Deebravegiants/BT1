### Title
Unbounded SVG document size/tag-count in `validateOption`/`tokenizeFile` enables CPU/memory exhaustion DoS on wallet icon rendering - ([File: libraries/svg-safe/src/validate.mjs])

### Summary
`validate()` in `libraries/svg-safe/src/validate.mjs` enforces a length cap of `50_000` only on the `d` attribute of `<path>` elements, but places no limit on the overall SVG document size, the number of tags, or the length of any other attribute. Since `validate()` is invoked synchronously on every `getIcon()` call in both `adapters/storage-icons-browser/src/icons-storage.js` and `adapters/storage-icons-mobile/src/icons-storage.js`, and `cleanup()`/`unzipIcon()` process attacker-influenced token icon data at store time, an attacker-controlled remote token/icon payload can force unbounded synchronous tokenization work.

### Finding Description
`tokenizeFile` [1](#0-0)  scans the whole raw SVG string character-by-character with no ceiling on total length or tag count, and `tokenizeLine`/`validateOption` are then applied to every single tag/attribute pair [2](#0-1) . The only explicit numeric length assertion in the whole module is the `path`/`d` check: [3](#0-2) 
No other attribute (`stop-color`, `points`, `values`, `transform`, `viewBox`, etc.) or the document as a whole has any size/count cap. `validate()` is reached from ordinary wallet flows: `getIcon` in `adapters/storage-icons-browser/src/icons-storage.js` calls `validate(icon)` directly on stored icon data [4](#0-3) , and the mobile equivalent does the same on file-read data [5](#0-4) . Icon payloads originate from `storeIcons(tokens)`, which decompresses/cleans attacker- or server-supplied `token.icon` values [6](#0-5) [7](#0-6) , i.e., a remote token-list/API response can inject a crafted SVG that later gets synchronously re-validated on every icon read. Because each attribute regex only bounds itself individually (and most, like `stop-color`, `values`, `points`-style attributes, have no length assert at all), an attacker can construct a multi-megabyte SVG with thousands of `<path>`, `<use>`, `<linearGradient>`, `<stop>` elements, each attribute just under whatever pattern applies, and no single check will reject it — `validate()` will linearly (or worse, due to repeated `indexOf`/`slice` calls) scan the entire payload.

### Impact Explanation
This is a Denial-of-Service on wallet responsiveness/availability, not a signing/key-compromise bug. A crafted multi-MB SVG causes `tokenizeFile`, `tokenizeLine`, and `validateOption` to run synchronously over the full input on the JS main thread (both browser and React Native adapters), which can block wallet UI, freeze the icon rendering pipeline, and degrade or halt wallet operations that share the same event loop while the icon list is loaded/re-validated. This matches a wallet-availability/DoS class of impact, not a fund-loss or key-exfiltration class impact.

### Likelihood Explanation
Preconditions: an attacker needs to control or influence the token/icon list content that is fed into `storeIcons`/`cleanup`/`validate` (e.g., a malicious or compromised remote token list / custom-token icon API response), which is explicitly one of the trust boundaries the question calls out. No privileged wallet state or user interaction beyond normal token list refresh is required, and the exploit is fully repeatable — every call to `getIcon()` for the stored malicious icon re-triggers the expensive validation. This is a plausible, low-complexity attack for any party able to supply icon data through the token/asset pipeline.

### Recommendation
Add an early, cheap document-level size/tag-count ceiling in `validate()`/`tokenizeFile` (e.g., reject raw SVG strings above a small max byte length such as a few KB, and cap the total number of tokens/tags) before any per-attribute regex work is performed, so oversized or attribute-count-abusive payloads fail fast instead of scaling with attacker-controlled input size.

### Proof of Concept
Fuzz/invariant test plan for `libraries/svg-safe/src/validate.mjs`:
1. Generate synthetic SVG strings with an increasing number of `<path d="…"/>` (each `d` just under 50,000 chars) and `<use>`/`<linearGradient>`/`<stop>` elements (each attribute just under its own regex's implicit limits), scaling total document size from 1MB to 50MB.
2. Assert that `validate()` throws or rejects once total input size/tag count exceeds a defined ceiling, rather than continuing to process the whole document.
3. Measure wall-clock time and memory of `validate(svg)` calls across the size range and assert execution time/memory scale sub-linearly-capped (bounded by a fixed ceiling) instead of growing unbounded with input size — a naive/current implementation is expected to fail this assertion, confirming no such document-level cap currently exists.

### Citations

**File:** libraries/svg-safe/src/validate.mjs (L16-38)
```javascript
function tokenizeFile(raw) {
  // Splits file into xml tags or text content
  assert(typeof raw === 'string', 'tokenizeFile: raw is not a string')
  const tokens = []
  let i = 0
  while (i < raw.length) {
    let j = raw.indexOf('<', i)
    if (j === i) {
      j = raw.indexOf('>', i)
      assert(j > i, 'tokenizeFile: > expected')
      j++
    } else if (j === -1) {
      j = raw.length
    }

    tokens.push(raw.slice(i, j))
    i = j
  }

  // Verify that we missed no characters
  assert(tokens.join('') === raw, 'tokenizeFile: characters are missing')
  return tokens
}
```

**File:** libraries/svg-safe/src/validate.mjs (L157-160)
```javascript
  if (tag === 'path' && name === 'd') {
    assert(value.length <= 50_000, `${tag} <path> too long`)
    if (/^[\d ,.ACHLMQSTVZacehlmqstvz-]+$/u.test(value)) return
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

**File:** adapters/storage-icons-browser/src/icons-storage.js (L12-28)
```javascript
  storeIcons = async (tokens) => {
    return Promise.all(
      tokens.map(async (token) => {
        const { icon, ...rest } = token

        if (isUndefined(icon)) return rest

        if (icon) {
          await this.#storeIcon(token)
        } else if (isNull(icon)) {
          await this.#deleteIcon(token)
        }

        return token
      })
    )
  }
```

**File:** adapters/storage-icons-browser/src/icons-storage.js (L30-34)
```javascript
  getIcon = async (assetName) => {
    const icon = await this.#iconsStorage.get(assetName)
    if (icon) validate(icon)
    return icon
  }
```

**File:** adapters/storage-icons-mobile/src/icons-storage.js (L42-49)
```javascript
  getIcon = async (assetName) => {
    const path = this.#getPath(assetName)
    const fileExists = await RNFS.exists(path)
    if (!fileExists) return null
    const data = await RNFS.readFile(path, 'utf8')
    validateSVG(data)
    return data
  }
```

**File:** adapters/storage-icons-browser/src/utils.js (L4-17)
```javascript
export const unzipIcon = async (base64) => {
  const buff = Buffer.from(base64, 'base64')
  const unzip = await new Promise((resolve, reject) => {
    gunzip(buff, (err, res) => {
      if (err) {
        reject(err)
        return
      }

      resolve(res)
    })
  })
  return cleanup(unzip.toString('utf8'))
}
```
