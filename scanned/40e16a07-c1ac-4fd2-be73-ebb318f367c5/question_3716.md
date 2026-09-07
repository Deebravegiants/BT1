# Q3716: Route confusion nep141:zec.omft.near + no `routeConfig` (default) (createWithdrawalIntents)

## Question
An integrator forwards a user's `assetId` = `nep141:zec.omft.near` (PoA-named token MIGRATED to Omni via `POA_TOKENS_MIGRATED_TO_OMNI_BRIDGE` (ChainKind.Zcash, UTXO chain)) with no `routeConfig` (default) into `IntentsSDK.createWithdrawalIntents`. Given that first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge, is there an input (destination, memo, or chain) for which the bridge that `supports()` selects differs from the bridge that later `createWithdrawalIdentifiers` selects for status, or from the custodian of the token, so the signed intent moves funds to a contract that never releases them?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (no `routeConfig` (default)), `destinationAddress`
- Exploit idea: first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge. Token specifics: PoA-named token MIGRATED to Omni via `POA_TOKENS_MIGRATED_TO_OMNI_BRIDGE` (ChainKind.Zcash, UTXO chain).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:zec.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep141:zec.omft.near` and no `routeConfig` (default), assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
