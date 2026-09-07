# Q0734: Route confusion nep141:base-0x833589fcd6edb6e08f4c7c32d4 + `createOmniBridgeRoute(chain)` nam (signAndSendWithdrawalIntent)

## Question
Trace `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` for `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near` (PoA factory ERC-20 (USDC on Base), prefix `base-`) under `createOmniBridgeRoute(chain)` naming a different chain than the token's origin: `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and only checks `getBridgedToken` != null. Can an unprivileged caller obtain a signed `IntentPrimitive[]` whose `receiver_id`/`recipient`/chain does not match the token's real bridge, without any bridge throwing, and does the SDK then report `completed`?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `assetId`, `routeConfig` (`createOmniBridgeRoute(chain)` naming a different chain than the token's origin), `destinationAddress`
- Exploit idea: `OmniBridge.supports` accepts any nep141 once `routeConfig.chain` is set and only checks `getBridgedToken` != null. Token specifics: PoA factory ERC-20 (USDC on Base), prefix `base-`.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with `nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near` and `createOmniBridgeRoute(chain)` naming a different chain than the token's origin, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
