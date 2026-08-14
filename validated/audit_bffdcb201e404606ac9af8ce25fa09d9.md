### Title
`purpose: 0` bypasses the `supportedPurposes` validation guard due to falsy-check - ([File: features/address-provider/module/address-provider.js])

### Summary
`AddressProvider.getAddress` and `getUnusedAddressIndexes` both use `if (purpose) { assert(supportedPurposes.includes(purpose)) }` to validate that a caller-supplied `purpose` is sanctioned for the asset/wallet account. Because `types.purpose` in `features/address-provider/module/validation.js` only enforces `'Number'` typing with no range/allow-list restriction, `purpose: 0` passes typeforce validation but is falsy in JS, so the `supportedPurposes.includes(purpose)` assertion is silently skipped.

### Finding Description
In `features/address-provider/module/address-provider.js`: [1](#0-0) 
the purpose-scoping check only runs `if (purpose)`. Since `0` is falsy, `getAddress({ ..., purpose: 0, ... })` skips straight past the `assert(supportedPurposes.includes(purpose), ...)` line and proceeds to call `baseAsset.api.getKeyIdentifier({ purpose, ... })` with the unvalidated `purpose: 0`.

The same pattern exists in `getUnusedAddressIndexes`: [2](#0-1) 

`types.purpose` in `validation.js` does nothing to prevent this, since it only requires the value be a `'Number'`: [3](#0-2) 

Whether this leads to actual out-of-policy key derivation depends on the specific asset's `getKeyIdentifier` implementation. For assets built with the shared `createGetKeyIdentifier` factory in `libraries/key-utils/src/key-identifier.js`, there is a secondary guard, `assertKeyIdentifierParameters`, which asserts `allowedPurposes.includes(purpose)` where `allowedPurposes` defaults to `[DEFAULT_PURPOSE]`: [4](#0-3) 
Since `DEFAULT_PURPOSE` is not `0` for standard coins, this secondary layer would independently reject `purpose: 0` for assets using this factory — meaning the practical exploitability of the bypass depends on whether an asset's `baseAsset.api.getKeyIdentifier` implementation performs its own purpose allow-listing. I was unable to fully verify every asset's custom `getKeyIdentifier` implementation (e.g., Cardano, Monero, Hedera use custom purposes per the test fixtures found) to confirm whether any of them omit such validation and would derive material under `purpose: 0` without rejection.

### Impact Explanation
The primary, explicitly documented guard intended to enforce "only supported purposes for the given asset/account are derivable" is bypassable via `purpose: 0` due to the falsy check, which is a genuine logic defect in `address-provider.js`. Whether this results in concrete wrong-account/wrong-purpose key derivation depends entirely on whether the specific asset's `getKeyIdentifier` implementation independently validates purpose. Assets using the shared `createGetKeyIdentifier` factory are protected by a second independent assertion; assets with bespoke `getKeyIdentifier` implementations may not be, in which case the impact would be derivation of an address/public key under an unsanctioned purpose (potentially aliasing unintended key material), matching the wrong-account access impact class.

### Likelihood Explanation
The vulnerable code path is directly reachable by any caller that can invoke `addressProvider.getAddress` or `getUnusedAddressIndexes` with `purpose: 0` — the precondition described in the question is accurate and unconditional (no additional access control gates this parameter). However, full exploitability (bypassing all downstream validation and producing a real key-material exposure) is asset-implementation-dependent, and I could not confirm a concrete asset where the downstream `getKeyIdentifier` lacks its own purpose allow-list check.

### Recommendation
Change `if (purpose)` to an explicit `if (purpose !== undefined)` (or `!isNil(purpose)`, matching the nil-check pattern already used elsewhere in the codebase, e.g. `mock.js`) in both `getAddress` and `getUnusedAddressIndexes` in `features/address-provider/module/address-provider.js`, so that `purpose: 0` is not silently treated as "no purpose supplied."

### Proof of Concept
Unit test plan in `features/address-provider/__tests__/module/`:
1. Pick/construct an asset whose `getSupportedPurposes` returns a list that does not include `0` (e.g., ethereum returns `[44]`, per `getSupportedPurposes() should return the list for ethereum` test).
2. Call `addressProvider.getAddress({ assetName: 'ethereum', walletAccount, purpose: 0, chainIndex: 0, addressIndex: 0 })`.
3. Assert the call is rejected (`await expect(...).rejects.toThrow(...)`), matching the same assertion message pattern used for other unsupported purposes (`purpose "${purpose}" is not supported for asset ...`).
4. Currently, this call would skip the `assert(supportedPurposes.includes(purpose))` in `address-provider.js` (lines 78–88) and proceed to `getKeyIdentifier`; the test should additionally verify at the `address-provider.js` level (independent of any downstream per-asset validation) that the purpose-scoping guard itself is enforced for `purpose: 0`.

### Citations

**File:** features/address-provider/module/address-provider.js (L78-88)
```javascript
    if (purpose) {
      const supportedPurposes = await this.#assetSources.getSupportedPurposes({
        walletAccount: walletAccountName,
        assetName,
      })

      assert(
        supportedPurposes.includes(purpose),
        `purpose "${purpose}" is not supported for asset "${assetName}" in wallet "${walletAccount}"`
      )
    }
```

**File:** features/address-provider/module/address-provider.js (L385-391)
```javascript
    if (purpose) {
      assert(
        purposes.includes(purpose),
        `purpose "${purpose}" is not supported for asset "${assetName}" in wallet "${walletAccount}"`
      )
      purposes = [purpose]
    }
```

**File:** features/address-provider/module/validation.js (L7-9)
```javascript
export const types = {
  purpose: 'Number',
  assetName: 'String',
```

**File:** libraries/key-utils/src/key-identifier.js (L13-39)
```javascript
export const assertKeyIdentifierParameters = (params, rules = {}) => {
  assert(isSafeObject(params), 'arguments for getKeyIdentifier were not an object')
  assert(isSafeObject(rules), 'rules for getKeyIdentifier were not an object')

  const {
    allowedPurposes = [DEFAULT_PURPOSE],
    allowedChainIndices = [DEFAULT_CHAIN_INDEX],
    allowMultipleAddresses = false,
    allowXPUB = false,
  } = rules

  assert(Array.isArray(allowedPurposes), 'rules.allowedPurposes has to be an array')
  assert(Array.isArray(allowedChainIndices), 'rules.allowedChainIndices has to be an array')
  assert(
    typeof allowMultipleAddresses === 'boolean',
    'rules.allowMultipleAddresses has to be a boolean'
  )
  assert(typeof allowXPUB === 'boolean', 'rules.allowXPUB has to be a boolean')

  const { purpose, accountIndex, chainIndex, addressIndex, compatibilityMode } = params

  assert(
    allowedPurposes.includes(purpose),
    `purpose was ${purpose}, which is not allowed. Can be one of the following: ${allowedPurposes.join(
      ', '
    )}`
  )
```
