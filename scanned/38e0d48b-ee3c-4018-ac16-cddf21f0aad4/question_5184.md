# Q5184: Route confusion nep141:lsd-usdt.rhealab.near + no `routeConfig` (default) (createWithdrawalIntents)

## Question
Trace `IntentsSDK.createWithdrawalIntents` for `nep141:lsd-usdt.rhealab.near` (in `FEE_SUBSIDIZED_TOKENS`; fee forced to 0 after the API returned one) under no `routeConfig` (default): first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (no `routeConfig` (default)), `destinationAddress`
- Exploit idea: first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge. Token specifics: in `FEE_SUBSIDIZED_TOKENS`; fee forced to 0 after the API returned one.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:lsd-usdt.rhealab.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep141:lsd-usdt.rhealab.near` and no `routeConfig` (default), assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
