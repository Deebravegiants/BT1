# Q4653: Route confusion nep141:starknet.omft.near + `createOmniBridgeRoute(chain)` nam (createWithdrawalIntents)

## Question
An integrator forwards a user's `assetId` = `nep141:starknet.omft.near` (MIGRATED to Omni (ChainKind.Strk)) with `createOmniBridgeRoute(chain)` naming a different chain than the token's origin into `IntentsSDK.createWithdrawalIntents`. Given that `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and only checks `getBridgedToken` != null, is there an input (destination, memo, or chain) for which the bridge that `supports()` selects differs from the bridge that later `createWithdrawalIdentifiers` selects for status, or from the custodian of the token, so the signed intent moves funds to a contract that never releases them?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (`createOmniBridgeRoute(chain)` naming a different chain than the token's origin), `destinationAddress`
- Exploit idea: `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and only checks `getBridgedToken` != null. Token specifics: MIGRATED to Omni (ChainKind.Strk).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:starknet.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep141:starknet.omft.near` and `createOmniBridgeRoute(chain)` naming a different chain than the token's origin, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
