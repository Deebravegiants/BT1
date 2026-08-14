Found it. `setPin` at `features/auth-mobile/module/auth.js#L115-122` calls `this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_PIN_KEY), value)` with **no `keyOpts`/`accessible` override**, unlike `#setBioAuth` which explicitly passes `{ accessible: ACCESSIBLE_WHEN_UNLOCKED_THIS_DEVICE_ONLY }` [1](#0-0) . Since `createMobileKeystore` defaults `accessible` to `reactNativeKeychain.ACCESSIBLE.WHEN_UNLOCKED` (not `ThisDeviceOnly`) whenever the caller doesn't supply `options`/`opts` [2](#0-1) , the user's PIN is written to the iOS Keychain with the plain `WHEN_UNLOCKED` accessibility class — which iOS **does** include in iTunes/iCloud backups (unlike `...ThisDeviceOnly` variants).

### Title
Mobile PIN stored in iOS Keychain without `ThisDeviceOnly` accessibility, exposing it to iTunes/iCloud backups - (File: `features/auth-mobile/module/auth.js`)

### Summary
`Auth.setPin` persists the user's 6-digit device PIN via `keystore.setSecret` without any accessibility options, so it inherits `keystore-mobile`'s default `ACCESSIBLE.WHEN_UNLOCKED` class instead of a `ThisDeviceOnly` variant, unlike the sibling `#setBioAuth` flow which explicitly hardens its keys.

### Finding Description
`createMobileKeystore` in `adapters/keystore-mobile/src/index.js` builds `defaultSetOptions` with `accessible: reactNativeKeychain.ACCESSIBLE.WHEN_UNLOCKED`, only overridden if the caller passes its own `options`/`opts` [3](#0-2) . `setSecret` merges per-call `opts` over these defaults [4](#0-3) .

`features/auth-mobile/module/auth.js` demonstrates the codebase is aware that sensitive keychain entries need `ThisDeviceOnly` protection: `#setBioAuth` explicitly sets `keyOpts = { accessible: ACCESSIBLE_WHEN_UNLOCKED_THIS_DEVICE_ONLY }` for the biometric/device-auth trigger keys [5](#0-4) . However, `setPin` calls `this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_PIN_KEY), value)` with no third argument at all [6](#0-5) , meaning the PIN falls back to the library default `WHEN_UNLOCKED` accessibility class rather than `AccessibleWhenUnlockedThisDeviceOnly`. On iOS, only `...ThisDeviceOnly` accessibility classes are excluded from encrypted device backups (iTunes/Finder and iCloud); plain `WHEN_UNLOCKED` items are backed up and restorable to another device.

This is the same root cause described in the Trail of Bits report against `RNEthersRS.swift`: keychain items are stored without an explicit `ThisDeviceOnly` accessibility class and therefore leak into backups.

### Impact Explanation
The stored value is the user's app-unlock PIN, used by `isCorrectPin` to gate wallet access [7](#0-6) . If an attacker with physical/passcode access to the device (or an attacker who compromises the user's iCloud account) extracts an iTunes/iCloud backup, the plaintext PIN can be recovered directly from the backup's Keychain export, allowing the attacker to unlock the wallet app and access wallet funds/keys gated behind this PIN. This is a concrete secret-disclosure / auth-bypass primitive matching the accepted impact classes.

### Likelihood Explanation
Exploitation requires either (a) physical device access plus device passcode knowledge to create a local backup, or (b) compromise of the user's iCloud credentials to fetch a cloud backup — both scenarios explicitly described in the original report as realistic, low-sophistication attack paths (password-reuse-based iCloud takeover at scale, or local device compromise). No additional wallet-specific privilege is needed beyond obtaining the backup.

### Recommendation
Pass an explicit `ThisDeviceOnly` accessibility option on every `keystore.setSecret` call that stores sensitive material, consistent with the pattern already used in `#setBioAuth`:
```js
await this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_PIN_KEY), value, {
  accessible: ACCESSIBLE_WHEN_UNLOCKED_THIS_DEVICE_ONLY,
})
```
Additionally, change `createMobileKeystore`'s `defaultSetOptions.accessible` in `adapters/keystore-mobile/src/index.js` to default to `WHEN_UNLOCKED_THIS_DEVICE_ONLY` so that any future/other callers that omit explicit options are safe by default, rather than relying on every call site to remember to opt in.

### Proof of Concept
1. Set a device PIN via `auth.setPin('123456')`; this internally calls `keystore.setSecret('auth:pin', '123456')` with no `accessible` option [6](#0-5) .
2. `createMobileKeystore`'s `setSecret` merges this against `defaultSetOptions = { accessible: ACCESSIBLE.WHEN_UNLOCKED }` and calls `reactNativeKeychain.setInternetCredentials('auth:pin', 'unused', '"123456"', { accessible: WHEN_UNLOCKED })` [8](#0-7)  — confirmed by the unit test asserting `{ accessible: 2 }` (i.e., `WHEN_UNLOCKED`) is used when no custom option is supplied [9](#0-8) .
3. On a real iOS device this keychain item, lacking a `ThisDeviceOnly` accessibility class, is included in an iTunes/Finder or iCloud backup of the device.
4. An attacker restoring/inspecting that backup (e.g., via a backup-extraction tool) recovers the item under key `auth:pin` and reads the plaintext 6-digit PIN, enabling direct unauthorized unlock of the wallet app on another device.

### Citations

**File:** features/auth-mobile/module/auth.js (L61-83)
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

**File:** features/auth-mobile/module/auth.js (L128-131)
```javascript
  isCorrectPin = async (input) => {
    const pin = await this.#keystore.getSecret(this.#key(AUTH_KEYSTORE_PIN_KEY))
    return !!pin && pin === input
  }
```

**File:** adapters/keystore-mobile/src/index.js (L16-42)
```javascript
  const defaultSetOptions = {
    accessible: reactNativeKeychain.ACCESSIBLE.WHEN_UNLOCKED,
    ...(platform === 'android'
      ? { securityLevel: reactNativeKeychain.SECURITY_LEVEL.SECURE_SOFTWARE }
      : {}),
    ...options,
  }

  const isKeystoreLockedAtom = createInMemoryAtom({ defaultValue: isLockedInitially })

  const awaitUnlocked = async () =>
    waitUntil({
      atom: isKeystoreLockedAtom,
      predicate: (isLocked) => !isLocked,
    })

  // custom set `opts` example:
  // https://github.com/exodusmovement/exodus-mobile/blob/73dc6a25d94696afdd64e9a3265bebd98507b9d6/src/_local_modules/app/wallet/rn.js#L224-L240
  const setSecret = async (key, value, opts = {}) => {
    await awaitUnlocked()
    validateKey(key)
    assert(value != null, 'value cannot be null or undefined')
    return reactNativeKeychain.setInternetCredentials(key, 'unused', BJSON.stringify(value), {
      ...defaultSetOptions,
      ...opts,
    })
  }
```

**File:** adapters/keystore-mobile/src/__tests__/index.test.js (L22-33)
```javascript
  it('sets, gets, deletes', async () => {
    await keystore.setSecret('voldemort kills', 'everyone')
    await expect(keystore.getSecret('voldemort kills')).resolves.toEqual('everyone')
    expect(reactNativeKeychain.setInternetCredentials).toHaveBeenCalledWith(
      'voldemort kills',
      'unused',
      '"everyone"',
      { accessible: 2 }
    )
    await keystore.deleteSecret('voldemort kills')
    await expect(keystore.getSecret('voldemort kills')).resolves.toEqual(undefined)
  })
```
