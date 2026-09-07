# Q5012: Route confusion nep141:eth.bridge.near + `createOmniBridgeRoute()` with no  (processWithdrawal)

## Question
Trace `IntentsSDK.processWithdrawal` for `nep141:eth.bridge.near` (Omni bridged ETH (`isBridgeToken`)) under `createOmniBridgeRoute()` with no chain: `OmniBridge.supports` requires a valid omni token or migrated PoA token, throws otherwise. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createOmniBridgeRoute()` with no chain), `destinationAddress`
- Exploit idea: `OmniBridge.supports` requires a valid omni token or migrated PoA token, throws otherwise. Token specifics: Omni bridged ETH (`isBridgeToken`).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:eth.bridge.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep141:eth.bridge.near` and `createOmniBridgeRoute()` with no chain, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
