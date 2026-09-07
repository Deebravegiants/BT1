# Q4854: Route confusion nep141:nbtc.bridge.near + `createOmniBridgeRoute(chain)` nam (processWithdrawal)

## Question
Trace `IntentsSDK.processWithdrawal` for `nep141:nbtc.bridge.near` (Omni native BTC (UTXO chain: `utxoMaxGasFee` + `utxoProtocolFee` added to amount, `MaxGasFee` msg)) under `createOmniBridgeRoute(chain)` naming a different chain than the token's origin: `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and only checks `getBridgedToken` != null. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `assetId`, `routeConfig` (`createOmniBridgeRoute(chain)` naming a different chain than the token's origin), `destinationAddress`
- Exploit idea: `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and only checks `getBridgedToken` != null. Token specifics: Omni native BTC (UTXO chain: `utxoMaxGasFee` + `utxoProtocolFee` added to amount, `MaxGasFee` msg).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:nbtc.bridge.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.processWithdrawal` with `nep141:nbtc.bridge.near` and `createOmniBridgeRoute(chain)` naming a different chain than the token's origin, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
