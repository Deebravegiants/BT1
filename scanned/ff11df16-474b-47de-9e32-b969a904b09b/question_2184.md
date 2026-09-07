# Q2184: Route confusion nep141:bch.omft.near + `createPoaBridgeRoute()` (createWithdrawalIntents)

## Question
An integrator forwards a user's `assetId` = `nep141:bch.omft.near` (PoA native BCH) with `createPoaBridgeRoute()` into `IntentsSDK.createWithdrawalIntents`. Given that `PoaBridge.supports` throws `UnsupportedAssetIdError` if the asset is not PoA, but migrated tokens return false silently, is there an input (destination, memo, or chain) for which the bridge that `supports()` selects differs from the bridge that later `createWithdrawalIdentifiers` selects for status, or from the custodian of the token, so the signed intent moves funds to a contract that never releases them?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (`createPoaBridgeRoute()`), `destinationAddress`
- Exploit idea: `PoaBridge.supports` throws `UnsupportedAssetIdError` if the asset is not PoA, but migrated tokens return false silently. Token specifics: PoA native BCH.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:bch.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep141:bch.omft.near` and `createPoaBridgeRoute()`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
