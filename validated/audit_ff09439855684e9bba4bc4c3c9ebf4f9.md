### Title
Weak default Keychain accessibility for stored secrets, including auth PIN, allows retrieval without user presence - ([File: adapters/keystore-mobile/src/index.js])

### Summary
The mobile keystore adapter that wraps the native iOS/Android keychain (`react-native-keychain`) sets a weak default accessibility level (`WHEN_UNLOCKED`) and never applies an `accessControl` (biometry/passcode gate) unless the caller explicitly passes one. The wallet's own PIN-setting code path (`Auth.setPin`) never supplies such options, so the local device PIN — the credential that gates unlocking the wallet/signing — is stored in the keychain without any user-presence check and without the strongest accessibility class that would also exclude it from device backups.

### Finding Description
`createMobileKeystore` in `adapters/keystore-mobile/src/index.js` builds `defaultSetOptions` with only `accessible: reactNativeKeychain.ACCESSIBLE.WHEN_UNLOCKED` (and, on Android, `SECURE_SOFTWARE` rather than the stronger `SECURE_HARDWARE`), with no `accessControl` set by default: [1](#0-0) 

Callers must explicitly opt in to stronger protection via the `opts` parameter of `setSecret`. In `features/auth-mobile/module/auth.js`, only the biometric/device-auth trigger keys are set with `accessControl` (`BiometryCurrentSet` / `UserPresence`): [2](#0-1) 

However, `setPin`, which stores the actual PIN value used by `isCorrectPin` to authenticate/unlock the wallet, calls `keystore.setSecret` with no options at all, meaning it falls back to the weak default (`WHEN_UNLOCKED`, no `accessControl`): [3](#0-2) 

This means the PIN secret can be read from the keychain by any code with keychain access as soon as the device is unlocked, without requiring the user to re-authenticate (Face ID/Touch ID/passcode) at the moment of access, and it is eligible for inclusion in device backups since `WHEN_UNLOCKED` (unlike `WHEN_PASSCODE_SET_THIS_DEVICE_ONLY`) is not the "this device only" tier tied to a set passcode.

### Impact Explanation
If the PIN value itself is exfiltrated (e.g., via a compromised backup, a malicious app with keychain access on a jailbroken device, or a backup-restore attack), an attacker gains the value checked by `isCorrectPin`, which the app uses to gate wallet unlock/signing flows. Combined with the lack of `accessControl` requiring live user presence, secrets are readable in the background without prompting the device owner, aligning with the reported exploit scenario: no user-presence check enables retrieval of the credential that authorizes signing.

### Likelihood Explanation
Exploitation requires local device compromise or backup access rather than a purely remote vector, so likelihood is bounded by physical/backup-level access assumptions similar to the original report's "Undetermined difficulty" classification. It is reachable in the current shipped code path (default options apply whenever a caller does not override them), not a mocked-only or hypothetical path.

### Recommendation
- In `adapters/keystore-mobile/src/index.js`, default to the strongest available accessibility (`WHEN_PASSCODE_SET_THIS_DEVICE_ONLY`) and require an explicit, intentional opt-out rather than opt-in for weaker settings, and use `SECURE_HARDWARE` by default on Android.
- In `features/auth-mobile/module/auth.js`, pass explicit `accessible`/`accessControl` options to `setPin` (and any other sensitive `setSecret` calls) consistent with the options already used for bio/device-auth trigger keys, so the PIN itself is protected by user presence, not just the derived trigger flags.
- Audit all `keystore.setSecret` call sites in the wallet/auth modules to ensure no sensitive value relies on the library default.

### Proof of Concept
1. Call `auth.setPin('123456')` as implemented in `features/auth-mobile/module/auth.js` (line 122): `this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_PIN_KEY), value)` — no `opts` passed.
2. This resolves to `createMobileKeystore.setSecret` in `adapters/keystore-mobile/src/index.js`, which merges only `defaultSetOptions` (`accessible: WHEN_UNLOCKED`, no `accessControl`) into the keychain write.
3. On a compromised/jailbroken device (or through backup extraction where `WHEN_UNLOCKED` items are included), the PIN item can be read from the keychain without any biometric/passcode prompt, since no `accessControl` was applied — unlike the `BIOMETRY_CURRENT_SET`/`UserPresence` protected trigger keys used for bio/device auth.

### Citations

**File:** adapters/keystore-mobile/src/index.js (L16-22)
```javascript
  const defaultSetOptions = {
    accessible: reactNativeKeychain.ACCESSIBLE.WHEN_UNLOCKED,
    ...(platform === 'android'
      ? { securityLevel: reactNativeKeychain.SECURITY_LEVEL.SECURE_SOFTWARE }
      : {}),
    ...options,
  }
```

**File:** features/auth-mobile/module/auth.js (L61-84)
```javascript
    const keyOpts = {
      accessible: ACCESSIBLE_WHEN_UNLOCKED_THIS_DEVICE_ONLY,
    }

    if (useDeviceAuth) {
      // Android and iOS handle `ACCESS_CONTROL_USER_PRESENCE` differently when device auth
      // is not enabled. This check ensures consistent behavior across platforms.
      const canAuth = await this.canUseDeviceAuth()
      if (!canAuth) {
        throw new DeviceAuthenticationUnavailableError()
      }

      await this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_DEVICE_AUTH_KEY), on, keyOpts)
      await this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_DEVICE_AUTH_TRIGGER_KEY), on, {
        ...keyOpts,
        accessControl: ACCESS_CONTROL_USER_PRESENCE, // This flag allows iOS to fallback to device pin.
      })
    } else {
      await this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_BIO_AUTH_KEY), on, keyOpts)
      await this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_BIO_AUTH_TRIGGER_KEY), on, {
        ...keyOpts,
        accessControl: ACCESS_CONTROL_BIOMETRY_CURRENT_SET,
      })
    }
```

**File:** features/auth-mobile/module/auth.js (L115-131)
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

  isCorrectPin = async (input) => {
    const pin = await this.#keystore.getSecret(this.#key(AUTH_KEYSTORE_PIN_KEY))
    return !!pin && pin === input
  }
```
