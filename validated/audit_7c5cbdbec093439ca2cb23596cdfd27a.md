### Title
`BioAuth.authenticate` (Android) returns the raw `RNBiometrics.authenticate()` result instead of a strict boolean, allowing a truthy-but-unsuccessful result to be treated as approval - ([File: features/auth-mobile/module/bio/bio-auth.android.js])

### Summary
On Android, `BioAuth.authenticate` awaits `RNBiometrics.authenticate(...)` and returns its resolved value verbatim on the success path, only normalizing to `false` on a thrown error. Since `@exodus/react-native-biometrics`'s `authenticate()` resolves (rather than throws) with an object such as `{ success: false, error: 'User cancellation' }` when the prompt is canceled/dismissed, that object is returned as-is by `BioAuth.authenticate`. Any caller that checks the return value only for truthiness (e.g. `if (await exodus.auth.bio.authenticate(...))`) will treat this non-throwing, unsuccessful object as an approved authentication, because a non-empty object is always truthy in JavaScript regardless of its `.success` field.

### Finding Description
`authenticate` is implemented as: [1](#0-0) 

The function does not check a `success` flag on the resolved object; it simply forwards whatever `RNBiometrics.authenticate` resolves with, and only substitutes `false` in the `catch` branch (i.e. only when the native call actually rejects/throws). The underlying `@exodus/react-native-biometrics` API is documented/known to resolve (not throw) with `{ success: false, error }` for user cancellation and similar non-error dismissal flows on Android, so this path is fully reachable by a user (or by anything simulating/dismissing the biometric prompt) without any native exception being raised.

This directly contrasts with the iOS counterpart, which is careful to normalize to strict booleans: [2](#0-1) 

The module is exposed publicly through the SDK surface as `exodus.auth.bio.authenticate`: [3](#0-2) 

Because the public contract of `authenticate()` is implicitly "truthy return means success" (as evidenced by the iOS implementation returning strict `true`/`false`), any external caller relying on that contract and doing a simple truthiness check (`if (await exodus.auth.bio.authenticate(...))`) will be fooled by the Android branch returning `{ success: false }` — a truthy object — for a canceled/failed biometric attempt.

### Impact Explanation
If a caller in the wallet application (in this repo or downstream) unlocks the wallet, exposes seed-derived data, or authorizes a signing operation based on a simple truthy check of `exodus.auth.bio.authenticate()`'s return value, an attacker (or even ordinary user error) who dismisses/cancels the Android biometric prompt without triggering a native throw can cause the wallet to treat this as a successful authentication. This is an auth bypass on the "locked means locked" invariant for biometric-only unlock, matching Hydra's auth-bypass / unauthorized-access impact category, since the return object is truthy while `.success` is `false`.

### Likelihood Explanation
This requires only: (1) `hasBioAuth` enabled and no PIN, matching the precondition stated in the question, and (2) the user/attacker pressing "cancel" or otherwise dismissing the Android biometric prompt, which is a normal user-controlled resolution path for `@exodus/react-native-biometrics` on Android (it resolves rather than rejects for cancellation). No special privileges or device compromise are needed — it's a standard native library resolution behavior that the wrapper fails to normalize.

Note: I was unable to locate an in-repo caller of `exodus.auth.bio.authenticate` that performs a bare truthiness check (no matches for `bio.authenticate(` or `auth.bio.authenticate` consumers were found in this repository), so the ultimate exploitability depends on how a consumer of this SDK module (likely in a different repo, e.g. the wallet UI application) uses the returned value. Within the scope of this repository, the defect is real and verifiable — the function does not enforce a strict boolean contract — but I could not confirm a concrete unlock/signing call site within this repo's codebase that would complete the full unlock-bypass chain.

### Recommendation
Normalize the Android implementation to return a strict boolean, mirroring the iOS module's contract:
```js
authenticate = async ({ title, subtitle, cancelButtonText }) => {
  const { hasDeviceAuth } = await this.#authAtom.get()
  try {
    const { success } = await RNBiometrics.authenticate({
      title,
      subtitle,
      cancelButtonText,
      fallbackToPasscode: hasDeviceAuth,
    })
    return success === true
  } catch (err) {
    this.#logger.warn('bioauth failed', getErrorProps(err))
    return false
  }
}
```

### Proof of Concept
Unit test plan for `features/auth-mobile/module/bio/bio-auth.android.js`:
1. Mock `@exodus/react-native-biometrics`'s `authenticate` to resolve (not throw) with `{ success: false, error: 'User cancellation' }`.
2. Construct `BioAuth` with a stub `authAtom.get()` returning `{ hasDeviceAuth: false }` and a stub logger.
3. Call `await bioAuth.authenticate({ title: 'Unlock' })`.
4. Current behavior: assert the returned value is the object `{ success: false, error: 'User cancellation' }`, which is truthy under `if (result)` — demonstrating the bug.
5. Expected/fixed behavior: assert `result === false` (strict boolean), so no caller can misinterpret a canceled/unsuccessful biometric prompt as an approval.

### Citations

**File:** features/auth-mobile/module/bio/bio-auth.android.js (L15-29)
```javascript
  authenticate = async ({ title, subtitle, cancelButtonText }) => {
    const { hasDeviceAuth } = await this.#authAtom.get()
    try {
      // explicitly awaits the promise to catch errors
      return await RNBiometrics.authenticate({
        title,
        subtitle,
        cancelButtonText,
        fallbackToPasscode: hasDeviceAuth,
      })
    } catch (err) {
      this.#logger.warn('bioauth failed', getErrorProps(err))
      return false
    }
  }
```

**File:** features/auth-mobile/module/bio/bio-auth.ios.js (L10-27)
```javascript
  authenticate = async () => {
    try {
      // loading the bioAuthTrigger will trigger the keychain security
      // if the user approves, it will succeed, if not it will throw
      const value = await this.#auth.getBioAuthTrigger()

      if (value === undefined) {
        await this.#auth.disableBioAuth()
        throw new BiometryChangedError()
      }

      return true
    } catch (e) {
      if (e instanceof BiometryChangedError) throw e

      return false
    }
  }
```

**File:** features/auth-mobile/api/index.js (L1-16)
```javascript
const authApiDefinition = {
  id: 'authApi',
  type: 'api',
  factory: ({ auth, authAtom, bioAuth, biometry }) => ({
    auth: {
      ...auth,
      async reload() {
        await auth.load()
      },
      bio: bioAuth,
      get: authAtom.get,
    },
  }),
  dependencies: ['auth', 'bioAuth', 'authAtom', 'biometry'],
}

```
