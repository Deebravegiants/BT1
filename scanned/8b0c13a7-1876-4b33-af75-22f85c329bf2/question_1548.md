# Q1548: Route confusion nep141:tron-d28a265909efecdcee7c50285852 + `createInternalTransferRoute()` (createWithdrawalIntents)

## Question
Trace `IntentsSDK.createWithdrawalIntents` for `nep141:tron-d28a265909efecdcee7c5028585214ea0b96f015.omft.near` (PoA TRC-20 USDT) under `createInternalTransferRoute()`: `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `assetId`, `routeConfig` (`createInternalTransferRoute()`), `destinationAddress`
- Exploit idea: `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks. Token specifics: PoA TRC-20 USDT.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:tron-d28a265909efecdcee7c5028585214ea0b96f015.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.createWithdrawalIntents` with `nep141:tron-d28a265909efecdcee7c5028585214ea0b96f015.omft.near` and `createInternalTransferRoute()`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
