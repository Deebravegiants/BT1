### Title
`changePassphraseOnNextWrite`/`changePassphrase` can silently fail to persist a passphrase rotation when followed by a no-op `set()` due to stale hash comparison - (File: `libraries/seco-keyval/src/index.js`)

### Summary
`SecoKeyval.batch()` compares a SHA-256 hash of the serialized in-memory data against `this._hash`, which was computed and cached under the *old* passphrase, and skips the actual `write()` call if the data content is unchanged. Since `changePassphraseOnNextWrite()` only swaps out `this._seco` (the read/write handler) without touching `this._hash` or forcing a write, a subsequent `set()`/`batch()` call with unchanged data will short-circuit and never invoke `this._seco.write()`, leaving the on-disk file encrypted with the old passphrase.

### Finding Description
`changePassphraseOnNextWrite` at [1](#0-0)  simply reconstructs `this._seco` with the new passphrase but does not reset `this._hash` nor force an immediate persisted write. The only method that actually forces a write regardless of hash is `changePassphrase()` itself [2](#0-1) , which calls `this._seco.write()` unconditionally. However, `changePassphraseOnNextWrite` is explicitly designed for callers to defer the write to a later, natural mutation (per its name/API in `features/wallet/module/wallet.js` and `features/application/src/api/index.ts`), and that later mutation goes through `batch()`.

`batch()` computes `hash = createHash('sha256').update(data).digest()` and only calls `await this._seco.write(...)` if `!this._hash.equals(hash)` [3](#0-2) . `this._hash` was last set on a previous write performed under the old passphrase. If the subsequent `set(key, value)` after `changePassphraseOnNextWrite()` writes an identical value (a legitimate no-op update, e.g. re-saving the same wallet metadata, re-selecting the same account, or any idempotent `set` call triggered by application logic), the computed hash matches `this._hash`, the `write()` branch is skipped, and `this._seco` (now configured with the new passphrase) is never actually invoked to persist anything. The file on disk remains encrypted with the old passphrase, while the in-memory `SecoKeyval` instance believes the passphrase change succeeded (no error is thrown, and `this._seco` internally holds the new passphrase for future non-no-op writes).

### Impact Explanation
A wallet/application flow that calls `changePassphraseOnNextWrite(newPassphrase)` (deferred passphrase rotation, e.g., during a "change PIN/password" flow that intends to bind the new passphrase on the next natural save) followed by any `set()`/`delete()` call that happens to leave `this._data`'s serialized form unchanged will silently fail to rotate the encryption-at-rest key. This undermines the credential-rotation invariant: the wallet's persisted keystore remains decryptable with the *old* passphrase indefinitely (until some future write actually changes content), even though the user/application believes the passphrase was successfully changed. This is a stale-credential-persistence issue directly matching a "privilege/credential persistence" class impact — an attacker or process retaining the old passphrase can continue to decrypt the wallet store after a purported passphrase change.

### Likelihood Explanation
Preconditions: `kv` is already opened and has written data at least once so `this._hash` is populated with a real hash from a prior write. The application must call `changePassphraseOnNextWrite` (not `changePassphrase`) and then perform a `set`/`delete`/`batch` operation whose net effect on `this._data` is unchanged (e.g., setting a key to its existing value, or a delete of a non-existent key). This is plausible in real call sites such as `features/wallet/module/wallet.js` and `features/application/src/modules/application.ts`, where a passphrase-change flow could be followed by routine state saves that are content-idempotent. The bug is deterministic and fully reproducible whenever the content-equality condition holds; it requires no privileged access, only a normal application code path.

### Recommendation
In `changePassphraseOnNextWrite`, force the hash to a sentinel value that never matches a future computed hash (e.g., reset `this._hash = Buffer.alloc(0)` or a random invalid buffer), so the next `batch()` call always performs a real `write()` regardless of content equality. Alternatively, have `changePassphraseOnNextWrite` set an internal `_pendingPassphraseChange` flag and modify `batch()` to bypass the hash-equality short-circuit whenever that flag is set, clearing it after a successful write.

### Proof of Concept
Integration test in `libraries/seco-keyval/src/seco-keyval.test.js` style:
1. `const kv = new SecoKeyval(file, header); await kv.open(oldPassphrase); await kv.set('foo', 'bar')` — this populates `this._hash` from a real write.
2. `kv.changePassphraseOnNextWrite(newPassphrase)`.
3. `await kv.set('foo', 'bar')` (same key/value — no-op content change).
4. Assert (bug reproduction): `const kv2 = new SecoKeyval(file, header); await kv2.open(oldPassphrase)` succeeds and `kv2.get('foo') === 'bar'`, proving the file is still encrypted with `oldPassphrase` despite the intended rotation.
5. Expected (fixed) behavior: `kv2.open(oldPassphrase)` should fail (decryption error), and `await (new SecoKeyval(file, header)).open(newPassphrase)` should succeed instead.

### Citations

**File:** libraries/seco-keyval/src/index.js (L59-64)
```javascript
    const data = Buffer.from(JSON.stringify(this._data))
    const hash = createHash('sha256').update(data).digest()
    if (!this._hash.equals(hash)) {
      this._hash = hash
      await this._seco.write(expand32k(gzipSync(data)))
    }
```

**File:** libraries/seco-keyval/src/index.js (L76-79)
```javascript
  changePassphraseOnNextWrite (newPassphrase: Buffer | string) {
    if (!this.hasOpened) throw new Error('Must open first.')
    this._seco = createSecoRW(this.file, newPassphrase, this.header)
  }
```

**File:** libraries/seco-keyval/src/index.js (L81-84)
```javascript
  async changePassphrase (newPassphrase: Buffer | string) {
    this.changePassphraseOnNextWrite(newPassphrase)
    await this._seco.write(expand32k(gzipSync(Buffer.from(JSON.stringify(this._data)))))
  }
```
