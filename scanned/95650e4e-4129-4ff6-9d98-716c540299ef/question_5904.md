# Q5904: Route confusion nep245:v2_1.omni.hot.tg:143_111111111111 + `createHotBridgeRoute(chain)` (createWithdrawalIntents)

## Question
An integrator forwards a user's `assetId` = `nep245:v2_1.omni.hot.tg:143_11111111111111111111` (HOT native MON; `MONAD_MAINNET_NETWORK_ID = 143` overrides omni-sdk's testnet mapping) with `createHotBridgeRoute(chain)` into `IntentsSDK.createWithdrawalIntents`. Given that `HotBridge.supports` ignores `routeConfig.chain` entirely and derives the chain from the nep245 token id, is there an input (destination, memo, or chain) for which the bridge that `supports()` selects differs from the bridge that later `createWithdrawalIdentifiers` selects for status, or from the custodian of the token, so the signed intent moves funds to a contract that never releases them?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (`createHotBridgeRoute(chain)`), `destinationAddress`
- Exploit idea: `HotBridge.supports` ignores `routeConfig.chain` entirely and derives the chain from the nep245 token id. Token specifics: HOT native MON; `MONAD_MAINNET_NETWORK_ID = 143` overrides omni-sdk's testnet mapping.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep245:v2_1.omni.hot.tg:143_11111111111111111111` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep245:v2_1.omni.hot.tg:143_11111111111111111111` and `createHotBridgeRoute(chain)`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
