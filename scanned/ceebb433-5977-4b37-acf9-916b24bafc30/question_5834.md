# Q5834: Route confusion nep245:v2_1.omni.hot.tg:143_111111111111 + no `routeConfig` (default) (signAndSendWithdrawalIntent)

## Question
With `assetId` = `nep245:v2_1.omni.hot.tg:143_11111111111111111111` (HOT native MON; `MONAD_MAINNET_NETWORK_ID = 143` overrides omni-sdk's testnet mapping) and no `routeConfig` (default), can an unprivileged caller of `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` make bridge selection pick a bridge or destination chain that does not custody this token (because first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `assetId`, `routeConfig` (no `routeConfig` (default)), `destinationAddress`
- Exploit idea: first bridge whose `supports()` is true wins, in order IntentsBridge, AuroraEngineBridge, PoaBridge, HotBridge, OmniBridge, DirectBridge. Token specifics: HOT native MON; `MONAD_MAINNET_NETWORK_ID = 143` overrides omni-sdk's testnet mapping.
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep245:v2_1.omni.hot.tg:143_11111111111111111111` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with `nep245:v2_1.omni.hot.tg:143_11111111111111111111` and no `routeConfig` (default), assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
