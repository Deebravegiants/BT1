# Q5715: Route confusion nep245:v2_1.omni.hot.tg:1100_111bzQBB5v7 + `createHotBridgeRoute(chain)` (createWithdrawalIntents)

## Question
Trace `IntentsSDK.createWithdrawalIntents` for `nep245:v2_1.omni.hot.tg:1100_111bzQBB5v7AhLyPMDwS8uJgQV24KaAPXtwyVWu2KXbbfQU6NXRCz` (HOT native XLM) under `createHotBridgeRoute(chain)`: `HotBridge.supports` ignores `routeConfig.chain` entirely and derives the chain from the nep245 token id. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (`createHotBridgeRoute(chain)`), `destinationAddress`
- Exploit idea: `HotBridge.supports` ignores `routeConfig.chain` entirely and derives the chain from the nep245 token id. Token specifics: HOT native XLM.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep245:v2_1.omni.hot.tg:1100_111bzQBB5v7AhLyPMDwS8uJgQV24KaAPXtwyVWu2KXbbfQU6NXRCz` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep245:v2_1.omni.hot.tg:1100_111bzQBB5v7AhLyPMDwS8uJgQV24KaAPXtwyVWu2KXbbfQU6NXRCz` and `createHotBridgeRoute(chain)`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
