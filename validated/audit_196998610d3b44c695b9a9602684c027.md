## Title
Android biometric authentication accepts newly-enrolled fingerprints without PIN re-verification, unlike iOS - ([File: features/auth-mobile/module/bio/bio-auth.android.js])

### Summary
The `@exodus/auth-mobile` feature implements biometric gating differently on iOS and Android. On iOS, the "trigger" secret used to gate bio-auth is stored with `ACCESS_CONTROL_BIOMETRY_CURRENT_SET` and read via `getBioAuthTrigger()`, so the OS invalidates that secret whenever the enrolled biometric set changes, forcing a fallback to PIN. On Android, `BioAuth.authenticate()` in `bio-auth.android.js` never checks or ties into any biometric-enrollment-invalidated secret — it simply calls `RNBiometrics.authenticate()` and trusts the boolean result, so a newly enrolled fingerprint (added after the wallet PIN/biometrics were originally set) will pass authentication and unlock bio-auth-protected actions with no PIN check.

### Finding Description
`auth.js`'s `#setBioAuth` stores two Android keystore secrets when bio-auth is enabled: `AUTH_KEYSTORE_BIO_AUTH_KEY` (plain accessible flag) and `AUTH_KEYSTORE_BIO_AUTH_TRIGGER_KEY`, the latter created with `accessControl: ACCESS_CONTROL_BIOMETRY_CURRENT_SET` [1](#0-0)  — this access control is exactly the primitive meant to invalidate the secret when the OS's enrolled biometric set changes.

On iOS, `BioAuth.authenticate()` actually reads this trigger secret via `auth.getBioAuthTrigger()`; if the OS has invalidated it (enrollment changed), the read returns `undefined`, bio-auth is disabled, and a `BiometryChangedError` is thrown, forcing PIN re-entry [2](#0-1) .

On Android, however, `BioAuth.authenticate()` does not read `getBioAuthTrigger()` or any keystore secret at all — it just forwards to `RNBiometrics.authenticate()` and returns whatever boolean that call produces, with no cross-check against biometric enrollment changes: [3](#0-2) . The `AUTH_KEYSTORE_BIO_AUTH_TRIGGER_KEY` secret with `ACCESS_CONTROL_BIOMETRY_CURRENT_SET` is written on Android too (same shared `#setBioAuth` code path), but it is never consulted by the Android `BioAuth` module, so its OS-level invalidation-on-enrollment-change semantic is effectively unused/wasted on that platform. This is the direct Android analog of HAL-07: the app trusts the device biometric prompt result without validating that the biometric data used to authenticate is the same as what was originally enrolled when the user set up bio-auth.

### Impact Explanation
An attacker with temporary physical access to an unlocked (or PIN/biometric-known) device can enroll their own fingerprint/face in Android system settings, then use it to pass `RNBiometrics.authenticate()` inside the wallet app and gain access to any feature gated purely by `bioAuth.authenticate()` (e.g., features depending on `shouldAuthenticate`/bio-auth flows for revealing mnemonics or authorizing signing), without ever knowing the user's PIN. This is a concrete auth-bypass / secret-disclosure risk consistent with the "Accept only concrete unauthorized signing, secret disclosure, auth bypass" validation bar.

### Likelihood Explanation
Requires an attacker to have temporary physical access to the unlocked device (or enough access to add a biometric enrollment) — an unprivileged-user local-access scenario, not a remote or privileged-operator attack, matching the low likelihood score (2/10) given in the original report while remaining in-scope as a legitimate unprivileged-user analog.

### Recommendation
On Android, mirror the iOS logic: read the `AUTH_KEYSTORE_BIO_AUTH_TRIGGER_KEY` secret (which is invalidated by `ACCESS_CONTROL_BIOMETRY_CURRENT_SET`) as part of `BioAuth.authenticate()`, and if that read fails/returns undefined, treat it as a `BiometryChangedError`, call `disableBioAuth()`, and force PIN re-authentication — the same pattern already implemented for iOS in `bio-auth.ios.js`.

### Proof of Concept
1. Set a PIN and enable biometrics in the app on Android (`auth.enableBioAuth()`).
2. On the device, go to system settings and enroll an additional fingerprint.
3. Trigger a bio-auth-gated action in the app; `BioAuth.authenticate()` in `bio-auth.android.js` calls `RNBiometrics.authenticate()`, which succeeds with the newly enrolled fingerprint.
4. Access is granted with no PIN prompt, because the Android `authenticate()` never checks the `AUTH_KEYSTORE_BIO_AUTH_TRIGGER_KEY` secret that would have been invalidated by the enrollment change.

### Citations

**File:** features/auth-mobile/module/auth.js (L78-84)
```javascript
    } else {
      await this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_BIO_AUTH_KEY), on, keyOpts)
      await this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_BIO_AUTH_TRIGGER_KEY), on, {
        ...keyOpts,
        accessControl: ACCESS_CONTROL_BIOMETRY_CURRENT_SET,
      })
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
