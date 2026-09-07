# Q3950: Route confusion nep141:sol.omft.near + `createOmniBridgeRoute()` with no  (processWithdrawal)

## Question
An integrator forwards a user's `assetId` = `nep141:sol.omft.near` (MIGRATED to Omni; `SOL_OMNI_CONTRACT_ID` with `MIN_AMOUNT_SOL_OMNI_WITHDRAWAL = 890880n`) with `createOmniBridgeRoute()` with no chain into `IntentsSDK.processWithdrawal`. Given that `OmniBridge.supports` requires a valid omni token or migrated PoA token, throws otherwise, is there an input (destination, memo, or chain) for which the bridge that `supports()` selects differs from the bridge that later `createWithdrawalIdentifiers` selects for status, or from the custodian of the token, so the signed intent moves funds to a contract that never releases them?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createOmniBridgeRoute()` with no chain), `destinationAddress`
- Exploit idea: `OmniBridge.supports` requires a valid omni token or migrated PoA token, throws otherwise. Token specifics: MIGRATED to Omni; `SOL_OMNI_CONTRACT_ID` with `MIN_AMOUNT_SOL_OMNI_WITHDRAWAL = 890880n`.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:sol.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep141:sol.omft.near` and `createOmniBridgeRoute()` with no chain, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
