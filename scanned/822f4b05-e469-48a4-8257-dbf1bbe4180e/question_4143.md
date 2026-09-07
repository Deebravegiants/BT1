# Q4143: Route confusion nep141:sol-5ce3bf3a31af18be40ba30f721101 + no `routeConfig` (default) (signAndSendWithdrawalIntent)

## Question
An integrator forwards a user's `assetId` = `nep141:sol-5ce3bf3a31af18be40ba30f721101b4341690186.omft.near` (MIGRATED USDC (Solana) to Omni) with no `routeConfig` (default) into `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`. Given that first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge, is there an input (destination, memo, or chain) for which the bridge that `supports()` selects differs from the bridge that later `createWithdrawalIdentifiers` selects for status, or from the custodian of the token, so the signed intent moves funds to a contract that never releases them?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `assetId`, `routeConfig` (no `routeConfig` (default)), `destinationAddress`
- Exploit idea: first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge. Token specifics: MIGRATED USDC (Solana) to Omni.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep141:sol-5ce3bf3a31af18be40ba30f721101b4341690186.omft.near` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with `nep141:sol-5ce3bf3a31af18be40ba30f721101b4341690186.omft.near` and no `routeConfig` (default), assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
