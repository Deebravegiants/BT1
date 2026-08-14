### Title
Race between `Auth.load()` and `Auth.setPin()`/`removePin()` can commit stale `hasPin`/`shouldAuthenticate` snapshot into `authAtom` - ([File: features/auth-mobile/module/auth.js])

### Summary
`Auth.load()` reads `hasPin`, bio-auth, and device-auth flags from the keystore *before* calling `#mergeIntoAtom`, and `#mergeIntoAtom` unconditionally overwrites `authAtom` fields with whatever was captured earlier, regardless of what has changed in the atom since that snapshot was taken. If `load()`'s keystore reads happen to complete before a concurrent `setPin()`/`removePin()`'s keystore write, but `load()`'s `#mergeIntoAtom` call is queued and applied to the atom *after* the concurrent operation's own `#mergeIntoAtom` call, the stale (pre-write) values stomp the just-committed values in `authAtom`, including `hasPin` and the derived `shouldAuthenticate`.

### Finding Description
`load()` performs several independent, unlocked `await` reads before merging: [1](#0-0) 

`#mergeIntoAtom` spreads the *previously captured* `params` object over whatever is currently in the atom at the moment `atom.set()`'s updater runs, so a fresher truth already stored in the atom can be overwritten by older data captured before this call started: [2](#0-1) 

`setPin()` writes the PIN secret to the keystore, then separately calls `#mergeIntoAtom({ hasPin: true })`: [3](#0-2) 

The underlying `@exodus/atoms` in-memory atom's `set()` is wrapped with `makeConcurrent` (default concurrency 1), which does serialize concurrent `atom.set()` invocations so each updater callback reads the *atom's own* current value atomically at invocation time: [4](#0-3) 

However, this only guarantees that each individual `#mergeIntoAtom` call is internally consistent — it does **not** prevent a `#mergeIntoAtom` call whose `params` were captured *before* the queue position from later being applied *after* a fresher `#mergeIntoAtom` call from a concurrent `setPin()`/`removePin()`. Concretely:

1. `load()` calls `this.hasPin()` and gets `false` because `setPin()`'s keystore write hasn't landed yet.
2. `setPin()` finishes its keystore write and calls `#mergeIntoAtom({ hasPin: true })`; this `atom.set()` call is queued and executes first, committing `hasPin: true`, `shouldAuthenticate: true`.
3. `load()` finishes its remaining reads (`#hasBioAuth()`, `#hasDeviceAuth()`, `biometry.get()`) and calls `#mergeIntoAtom({ hasPin: false, biometry, hasBioAuth, hasDeviceAuth })` with the stale `hasPin: false` captured in step 1. This `atom.set()` call runs after step 2's, and the updater does `{ ...current, ...params }`, so `params.hasPin = false` overwrites the just-committed `current.hasPin = true`.
4. The atom recomputes `shouldAuthenticate = hasDeviceAuth || hasBioAuth || hasPin`, all now false, so `shouldAuthenticate` becomes `false` even though a PIN was just set and its secret is present in the keystore.

There is no mutex/version-check around the entire read → merge sequence in `load()`, `setPin()`, or `removePin()` to prevent this stale-overwrite; only the atom's own internal `set()` call is serialized, which is insufficient here because the staleness originates in the input parameters, not in the atom's internal compute step.

### Impact Explanation
If `authAtom.shouldAuthenticate` is falsely `false` after the user has just set (or the wallet has just persisted) a PIN, any consumer relying on this atom (e.g., lock-screen/UI gating logic) could treat the wallet as unlocked or as having no PIN configured, weakening the "locked means locked" invariant. This affects local UI auth-gating state, not the underlying keystore secrets themselves (the PIN secret is still correctly written to the keystore regardless of the atom race), so the practical impact is scoped to bypassing the app's own auth-state signal used to decide whether to show/require a PIN prompt.

### Likelihood Explanation
Triggering the race requires two specific auth-module calls to be in flight concurrently with a particular ordering: `load()`'s keystore reads must complete *before* `setPin()`/`removePin()`'s keystore write, but `load()`'s `#mergeIntoAtom` invocation must be queued to run *after* the other operation's. Whether this is realistically reachable from an unprivileged, untrusted dapp/origin depends on whether `auth.load`, `auth.setPin`, and `auth.removePin` are exposed on an RPC/bridge surface callable by external/dapp code — this exposure could not be confirmed from the available context (the `features/auth-mobile/api/index.js` and `plugin/index.js` files that reference `authAtom` were not fully inspected). If these methods are only invokable from trusted internal wallet UI flows (e.g., only triggered by the user's own PIN-entry screen), the practical attacker-reachability from "ordinary dapp/origin requests" as required by the rules is weak; the race is real and reproducible as an internal concurrency defect, but its qualification as an externally-triggerable "attacker" bug is uncertain without confirming RPC exposure.

### Recommendation
Make `load()`'s snapshot-and-merge atomic with respect to concurrent `setPin()`/`removePin()`/`enableBioAuth()`/`disableBioAuth()` calls, e.g., by having `#mergeIntoAtom` re-read the relevant keystore values from within the `authAtom.set()` updater itself (so all reads happen under the same serialized `set()` invocation), or by wrapping all mutating auth methods with a shared `makeConcurrent`-style mutex so that `load()` cannot interleave with any secret-writing operation.

### Proof of Concept
Integration test (Jest) using the existing test harness structure in `features/auth-mobile/module/__tests__/auth.test.js`:
```js
test('concurrent load() and setPin() never leave authAtom stale', async () => {
  // Simulate load()'s keystore read for hasPin resolving slowly, so it captures
  // hasPin=false before setPin's write lands, but its mergeIntoAtom call
  // still gets queued after setPin's.
  const originalGetSecret = keystore.getSecret
  let callCount = 0
  keystore.getSecret = jest.fn(async (k) => {
    callCount++
    if (k === key(AUTH_KEYSTORE_PIN_KEY) && callCount === 1) {
      await new Promise((r) => setTimeout(r, 10)) // delay first hasPin() read
    }
    return originalGetSecret(k)
  })

  await Promise.all([auth.load(), auth.setPin('123456')])

  const finalState = await authAtom.get()
  const keystoreHasPin = !!(await keystore.getSecret(key(AUTH_KEYSTORE_PIN_KEY)))

  // Assert authAtom state matches the actually committed keystore secret
  expect(finalState.hasPin).toBe(keystoreHasPin)
  expect(finalState.shouldAuthenticate).toBe(
    finalState.hasPin || finalState.hasBioAuth || finalState.hasDeviceAuth
  )
})
```
Expected (buggy) result: `finalState.hasPin` is `false` while `keystoreHasPin` is `true`, demonstrating the stale overwrite; a fixed implementation should keep them consistent across repeated `Promise.all([auth.load(), auth.setPin(...)])` runs.

### Citations

**File:** features/auth-mobile/module/auth.js (L87-94)
```javascript
  load = async () => {
    const hasPin = await this.hasPin()
    const hasBioAuth = await this.#hasBioAuth()
    const hasDeviceAuth = await this.#hasDeviceAuth()
    const biometry = await this.#biometry.get()

    await this.#mergeIntoAtom({ hasPin, biometry, hasBioAuth, hasDeviceAuth })
  }
```

**File:** features/auth-mobile/module/auth.js (L96-113)
```javascript
  #mergeIntoAtom = async (params) => {
    await this.#authAtom.set((current) => {
      const data = {
        ...current,
        ...params,
      }

      const { hasBioAuth, biometry, hasPin, hasDeviceAuth } = data

      data.hasBioAuth = hasBioAuth && !!biometry
      data.shouldAuthenticate = hasDeviceAuth || hasBioAuth || hasPin

      if (isEqual(current, data)) return current

      this.#logger.info('Updated auth data', data)
      return data
    })
  }
```

**File:** features/auth-mobile/module/auth.js (L115-126)
```javascript
  setPin = async (value) => {
    value = value.trim()

    if (value.length !== 6) {
      throw new InvalidPasscodeLengthError()
    }

    await this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_PIN_KEY), value)
    await this.#mergeIntoAtom({ hasPin: true })

    await this.#eventLog.record({ event: 'pin_auth_set' })
  }
```

**File:** libraries/atoms/src/enforce-rules.ts (L96-106)
```typescript
  const set = makeConcurrent(async (value: T | ((value: T) => T)) => {
    // support a function a la React's setState(oldState => newState)
    if (isSetter(value)) {
      const current = getInitialized() ? await get() : defaultValue
      value = await value(current)

      if (current === value) return
    }

    await atom.set(value)
  })
```
