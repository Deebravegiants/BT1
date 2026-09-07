# Q2913: Route confusion nep141:gnosis-0xe91d153e0b41518a2ce8dd3d + `createPoaBridgeRoute()` (processWithdrawal)

## Question
Trace `IntentsSDK.processWithdrawal` for `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` (PoA ERC-20 on Gnosis) under `createPoaBridgeRoute()`: `PoaBridge.supports` throws `UnsupportedAssetIdError` if the asset is not PoA, but migrated tokens return false silently. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createPoaBridgeRoute()`), `destinationAddress`
- Exploit idea: `PoaBridge.supports` throws `UnsupportedAssetIdError` if the asset is not PoA, but migrated tokens return false silently. Token specifics: PoA ERC-20 on Gnosis.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` and `createPoaBridgeRoute()`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
