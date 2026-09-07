# Q5765: Route confusion nep245:v2_1.omni.hot.tg:9745_11111111111 + `createInternalTransferRoute()` (processWithdrawal)

## Question
Trace `IntentsSDK.processWithdrawal` for `nep245:v2_1.omni.hot.tg:9745_11111111111111111111` (HOT native XPL; `gasPrice *= 100n` for non-native tokens on Plasma) under `createInternalTransferRoute()`: `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createInternalTransferRoute()`), `destinationAddress`
- Exploit idea: `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks. Token specifics: HOT native XPL; `gasPrice *= 100n` for non-native tokens on Plasma.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep245:v2_1.omni.hot.tg:9745_11111111111111111111` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep245:v2_1.omni.hot.tg:9745_11111111111111111111` and `createInternalTransferRoute()`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
