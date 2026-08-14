### Title
Path validation bypass in `#deleteIcon` allows path traversal / arbitrary file deletion via crafted token name - ([File: adapters/storage-icons-mobile/src/icons-storage.js])

### Summary
In `adapters/storage-icons-mobile/src/icons-storage.js`, `IconsStorage#storeIcon` validates the asset name against `iconNameRegex` via the shared `#getPath()` helper before writing a file, but `#deleteIcon` builds the file path with a raw template string (`${this.#iconsDirectory}/${assetName}.svg`) and never calls `#getPath()` or validates against `iconNameRegex`. Since `assetName` comes from `token.name || token.assetName`, and tokens reach `storeIcons` from remote custom-token registry (CTR) responses (`fetchToken`, `#fetchTokens`, `#fetchUpdates`, `addRemoteTokens` in `features/assets-feature/module/assets-module.js`), a crafted `name`/`assetName` containing path traversal sequences (e.g. `../otherAccountAsset`) combined with `icon: null` can cause `RNFS.unlink` to be invoked on an attacker-chosen path relative to the icons directory.

### Finding Description
`#storeIcon` computes its path via `this.#getPath(assetName)`, which asserts `iconNameRegex.test(assetName)` (`adapters/storage-icons-mobile/src/icons-storage.js:72-75`) before writing. `#deleteIcon`, however, computes the path directly:
```js
#deleteIcon = async (token) => {
  const assetName = token.name || token.assetName
  const path = `${this.#iconsDirectory}/${assetName}.svg`
  ...
}
```
(`adapters/storage-icons-mobile/src/icons-storage.js:58-66`)

`storeIcons` (lines 26-40) dispatches to `#deleteIcon` whenever `isNull(token.icon)` is true, regardless of the token's origin. Tokens flow into `storeIcons` from CTR/network responses processed in `features/assets-feature/module/assets-module.js` (`#storeIcons` called from `fetchToken`, `#fetchTokens`, `#fetchUpdates`, `addRemoteTokens`) after `validateCustomToken`/`isValidCustomToken` schema checks and `normalizeToken` (which sets `name: token.name || token.assetName`). These validations check token schema shape but there is no evidence in the reachable code that the `name`/`assetName` field is constrained to the `iconNameRegex` pattern before being handed to the icons storage adapter — that check exists only inside `#getPath()`, which `#deleteIcon` skips entirely. This is an inconsistency between the two sibling methods (`#storeIcon` vs `#deleteIcon`) in the same class, confirming that the intended security boundary (`iconNameRegex`) is bypassed for deletions specifically.

Because `RNFS.unlink` operates on whatever path string is produced, an attacker-controlled asset name of the form `../otherAccountAsset` (or deeper `../../` sequences) would cause `path` to resolve outside `this.#iconsDirectory`, letting the delete operation target a sibling or ancestor file, e.g. another account's/asset's cached icon file, on the filesystem.

### Impact Explanation
This allows an unprivileged remote-content path (crafted CTR/custom-token response, or any token descriptor a user can trigger the app to fetch, e.g. `addToken`/`addRemoteTokens`) to delete or corrupt files outside the intended icons cache scope via directory traversal in the deletion path, breaking the invariant that "persisted state is authentic" for the icon cache. Scoped impact is cache corruption/DoS (forced re-fetch, missing/incorrect icon display, or deletion of an arbitrary file reachable via relative traversal from the icons directory) — not key/secret compromise or signing bypass.

### Likelihood Explanation
Feasibility is straightforward: any code path that calls `storeIcons`/`#storeIcons` with a token whose `name`/`assetName` is attacker-influenced and `icon: null` triggers `#deleteIcon` without any regex/path validation, unlike `#storeIcon`. No authentication or privileged state is required beyond causing the app to process a custom-token entry with a crafted name (e.g., via CTR response, `addToken`, or `addRemoteTokens`). The bug is 100% reproducible given such an input, since `#deleteIcon` never calls `#getPath()`/`iconNameRegex`.

### Recommendation
Make `#deleteIcon` use the same validated path resolution as `#storeIcon`: call `const path = this.#getPath(assetName)` in `#deleteIcon` (removing the raw template-string path construction), so the `iconNameRegex` assertion in `#getPath()` is enforced identically for both store and delete operations.

### Proof of Concept
Unit test in `adapters/storage-icons-mobile/src/__tests__/icons-storage.test.js` (or equivalent):
```js
it('rejects path traversal in deleteIcon', async () => {
  const storage = createIconsStorage({ config: { iconsPath: 'icons', customTokensIconsEnabled: true }, logger })
  await expect(
    storage.storeIcons([{ name: '../otherAccountAsset', icon: null }])
  ).rejects.toThrow(/invalid characters/)
  // Assert RNFS.unlink was never called with a path outside the icons directory
  expect(RNFS.unlink).not.toHaveBeenCalledWith(expect.stringContaining('../'))
})
```
Expected (current, failing) behavior: `#deleteIcon` builds `path = "<iconsDirectory>/../otherAccountAsset.svg"` and calls `RNFS.exists`/`RNFS.unlink` on it without throwing, since `iconNameRegex` is never checked. After the fix (using `#getPath()` in `#deleteIcon`), the same call should throw `'token name contains invalid characters'` exactly as `#storeIcon` does, and `RNFS.unlink` should never be invoked with a traversal path. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** adapters/storage-icons-mobile/src/icons-storage.js (L26-40)
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
```

**File:** adapters/storage-icons-mobile/src/icons-storage.js (L51-75)
```javascript
  #storeIcon = async (token) => {
    const assetName = token.name || token.assetName
    const path = this.#getPath(assetName)
    const svg = await unzipIcon(token.icon)
    await RNFS.writeFile(path, svg, 'utf8')
  }

  #deleteIcon = async (token) => {
    const assetName = token.name || token.assetName
    const path = `${this.#iconsDirectory}/${assetName}.svg`
    const res = await RNFS.exists(path)
    if (res) {
      await RNFS.unlink(path)
      this.#logger?.debug(`${assetName} icon deleted`)
    }
  }

  #ensureIconsDir = async () => {
    return RNFS.mkdir(this.#iconsDirectory, { NSURLIsExcludedFromBackupKey: true })
  }

  #getPath = (assetName) => {
    assert(iconNameRegex.test(assetName), 'token name contains invalid characters')
    return `${this.#iconsDirectory}/${assetName}.svg`
  }
```

**File:** features/assets-feature/module/assets-module.js (L37-42)
```javascript
const normalizeToken = (token) => ({
  ...token,
  name: token.name || token.assetName,
  displayName: token.displayName || token.properName, // eslint-disable-line @exodus/hydra/no-asset-proper
  displayTicker: token.displayTicker || token.properTicker, // eslint-disable-line @exodus/hydra/no-asset-proper
})
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
