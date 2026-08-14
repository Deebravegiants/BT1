### Title
Unbounded gzip decompression of custom-token icons in `unzipIcon` allows CPU/memory exhaustion before `cleanup()`/`validate()` run - ([File: adapters/storage-icons-browser/src/utils.js], [File: adapters/storage-icons-mobile/src/icons-storage.js], [File: libraries/svg-safe/src/cleanup.mjs])

### Summary
Custom token icons fetched from the Custom Token Registry (CTR) are gzip-decompressed with no output size cap before being handed to `cleanup()`, which runs three unbounded regex `.replace()` passes, followed by `validate()`'s per-character tokenizer. A malicious or attacker-registered custom token with a small gzip "bomb" icon can force multi-megabyte-to-gigabyte string allocation and CPU-heavy regex/tokenization work inside `#storeIcon`/`storeIcons`.

### Finding Description
`AssetsModule.addToken`/`addTokens`/`addRemoteTokens`/`searchTokens`/`fetchToken`/`#fetchTokens` fetch token definitions (including `token.icon`, an attacker-controlled base64(gzip(svg)) string) from the CTR server via `this.#fetch(...)` [1](#0-0) , run only schema-shape validation via `validateCustomToken`, and then call `#storeIcons(tokens)` [2](#0-1) .

Icon storage then calls `unzipIcon(token.icon)`. In the browser adapter this is `Buffer.from(base64,'base64')` → Node `zlib.gunzip` with no `maxOutputLength` option → `cleanup(unzip.toString('utf8'))` [3](#0-2) . In the mobile adapter it is synchronous `pako.ungzip(arr, { to: 'string' })` with no size limit → `cleanupSVG(str)` [4](#0-3) .

`cleanup()` then performs three global regex `.replace()` passes over the full decompressed string before calling `validate()` [5](#0-4) , and `validate()` character-walks the whole string via `tokenizeFile`/`tokenizeLine` [6](#0-5) [7](#0-6) . None of these steps impose a length cap on the decompressed SVG string before doing this work — the only length bound found in `validate.mjs` is a `50_000` character cap on `<path d="...">` values [8](#0-7) , which only applies after tokenization/parsing has already happened, i.e. after the expensive work is done.

No size limit was found on `token.icon` in the schema/shape validation path reachable before `unzipIcon` is invoked (searches for the `asset-schema-validation` package sources returned no results in the index, and `validateCustomToken` is only referenced, not defined, in the reachable code). Gzip compression ratios of >1000x are trivial to construct, so a few KB of attacker-controlled base64 data can decompress to hundreds of MB or more, all processed synchronously in the wallet's JS runtime (this is especially severe on mobile, where `pako.ungzip` runs synchronously on the app's single JS thread that also drives UI/wallet operations).

### Impact Explanation
This is an availability/DoS issue: adding or refreshing a malicious custom token (via `addToken`, `addTokens`, `addRemoteTokens`, or the periodic `updateTokens`/`#fetchUpdates` path) can cause excessive memory allocation and CPU-bound regex/tokenization work in the wallet process. On mobile this blocks the single JS thread that also services wallet UI and background token/asset operations, degrading or freezing app responsiveness. This does not itself lead to key disclosure or unauthorized signing, so it should be scoped as a **Denial-of-Service / availability** finding rather than a fund-loss or signing-bypass vulnerability.

### Likelihood Explanation
Preconditions: the CTR (`customTokensServerUrl`, default `CT_DEFAULT_SERVER`) must return (or be tricked into returning, e.g. via a public/anyone-can-submit custom-token registry, or a compromised/malicious response) a token entry whose `icon` field is a crafted gzip bomb. Given custom token registries typically accept community submissions for lookup/search (`searchTokens`, `addRemoteTokens`), this is a realistic, repeatable, low-effort attack once such a token is listed and a user attempts to view/add/search it. This is feasible without any privileged wallet state or social engineering beyond a user browsing/adding a custom token, which is a normal application flow.

### Recommendation
Enforce a hard byte-size cap on `token.icon` (base64/gzip length) prior to decompression, and additionally use a bounded decompression API (e.g. Node's `zlib.gunzip` with a `maxOutputLength` option / manual streaming with an accumulated-size cutoff, and an equivalent explicit length check for `pako.ungzip`) that aborts once decompressed output exceeds a small fixed limit (e.g. a few tens of KB, consistent with typical icon SVG sizes). This cap should be enforced in `unzipIcon` (both `adapters/storage-icons-browser/src/utils.js` and `adapters/storage-icons-mobile/src/icons-storage.js`) before `cleanup()` is ever invoked, and ideally also validated earlier at the schema-validation layer (`validateCustomToken`) on the raw `icon` field length.

### Proof of Concept
Unit/fuzz test plan for `adapters/storage-icons-browser/src/utils.js` and `adapters/storage-icons-mobile/src/icons-storage.js`:
1. Construct a gzip bomb: generate a large repetitive SVG-shaped string (e.g. 200MB of `<!-- ... -->` filler or repeated whitespace) and gzip it; base64-encode the compressed bytes (compressed size should be under a few KB).
2. Call `unzipIcon(base64Bomb)` and assert that:
   - Either the call throws/rejects with a "payload too large" error before or during decompression, **or**
   - Measure wall-clock time and peak memory (e.g. via `process.memoryUsage()` before/after) and assert they stay under fixed thresholds (e.g. <10MB allocated, <50ms), which currently fails because decompression proceeds unbounded.
3. Fuzz with varying decompressed target sizes (1MB, 10MB, 100MB, 1GB-equivalent bomb) and assert a hard cap rejects requests above a defined threshold — currently no such cap exists, so all sizes succeed and pass through to `cleanup()`/`validate()`, confirming the missing STORAGE_INTEGRITY bound.

### Citations

**File:** features/assets-feature/module/assets-module.js (L258-291)
```javascript
    const getCustomTokensDefinitions = async (descriptors) => {
      const _tokens = await this.#fetch(
        `tokens`,
        { assetIds: descriptors, lifecycleStatus: ['c', 'v', 'u'] },
        'tokens'
      )

      let validTokens = []
      if (this.#shouldValidateCustomToken) {
        for (const token of _tokens) {
          try {
            validateCustomToken(token)
            validTokens.push(token)
          } catch (e) {
            this.#logger.warn(
              `Token did not pass validation ${token.baseAssetName} ${token.assetId}. Error: ${e.message}`
            )
          }
        }
      } else {
        validTokens = _tokens
      }

      const tokens = validTokens.map((token) => normalizeToken(token))

      await this.#storeIcons(tokens)

      for (const token of tokens) {
        const key = getFetchCacheKey(token.baseAssetName, token.assetId)
        this.#setCache(key, token)
      }

      return tokens
    }
```

**File:** features/assets-feature/module/assets-module.js (L676-687)
```javascript
  #storeIcons = async (tokens) => {
    try {
      if (tokens.length > 0) {
        await this.#iconsStorage.storeIcons(tokens)
      }
    } catch (err) {
      this.#logger.warn(
        `An error occurred while storing icons ${tokens.map((t) => t.name).join(',')}`,
        err
      )
    }
  }
```

**File:** adapters/storage-icons-browser/src/utils.js (L1-17)
```javascript
import { gunzip } from 'zlib'
import { cleanup } from '@exodus/svg-safe'

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

**File:** libraries/svg-safe/src/validate.mjs (L16-66)
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

function tokenizeLine(raw) {
  // Splits file into xml tags or text content
  assert(typeof raw === 'string', 'tokenizeLine: raw is not a string')
  assert(raw.startsWith('<') && raw.endsWith('>'), 'tokenizeLine: invalid raw start/end tags')
  let i = raw.indexOf(' ')
  if (i < 0) i = raw.length - 1
  const tokens = []
  tokens.push(raw.slice(1, i))
  while (i < raw.length - 1) {
    let j = raw.indexOf('"', i)
    if (j === -1) {
      j = raw.length - 1
      if (i !== j) tokens.push(raw.slice(i, j))
      i = j
    } else {
      assert(j > i, 'tokenizeLine: invalid j > i')
      const k = raw.indexOf('"', j + 1)
      assert(k > j, 'tokenizeLine: invalid k > j')
      tokens.push(raw.slice(i, k + 1))
      i = k + 1
    }
  }

  // Verify that we missed no characters
  assert(`<${tokens.join('')}>` === raw, 'tokenizeLine: missed characters')
  return tokens
}
```

**File:** libraries/svg-safe/src/validate.mjs (L157-159)
```javascript
  if (tag === 'path' && name === 'd') {
    assert(value.length <= 50_000, `${tag} <path> too long`)
    if (/^[\d ,.ACHLMQSTVZacehlmqstvz-]+$/u.test(value)) return
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
