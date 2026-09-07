# Q1037: Route confusion nep141:arb-0xaf88d065e77c8cc2239327c5edb + `createPoaBridgeRoute()` (processWithdrawal)

## Question
Trace `IntentsSDK.processWithdrawal` for `nep141:arb-0xaf88d065e77c8cc2239327c5edb3a432268e5831.omft.near` (PoA ERC-20 on Arbitrum) under `createPoaBridgeRoute()`: `PoaBridge.supports` throws `UnsupportedAssetIdError` if the asset is not PoA, but migrated tokens return false silently. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createPoaBridgeRoute()`), `destinationAddress`
- Exploit idea: `PoaBridge.supports` throws `UnsupportedAssetIdError` if the asset is not PoA, but migrated tokens return false silently. Token specifics: PoA ERC-20 on Arbitrum.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:arb-0xaf88d065e77c8cc2239327c5edb3a432268e5831.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep141:arb-0xaf88d065e77c8cc2239327c5edb3a432268e5831.omft.near` and `createPoaBridgeRoute()`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
