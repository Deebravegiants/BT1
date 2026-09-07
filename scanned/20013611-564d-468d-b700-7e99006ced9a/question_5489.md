# Q5489: Route confusion nep245:v2_1.omni.hot.tg:137_2791bca1f2de + `createInternalTransferRoute()` (signAndSendWithdrawalIntent)

## Question
With `assetId` = `nep245:v2_1.omni.hot.tg:137_2791bca1f2de4661ed88a30c99a7a9449aa84174` (HOT ERC-20 on Polygon (USDC.e)) and `createInternalTransferRoute()`, can an unprivileged caller of `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` make bridge selection pick a bridge or destination chain that does not custody this token (because `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks), so the emitted `ft_withdraw`/`mt_withdraw`/`transfer` carries `receiver_id`/`recipient` for the wrong contract or chain and the funds are burned or stranded?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `IntentsSDK.bridges` ordering, `createWithdrawalIntents`; bridge `supports()` / `parseAssetId()` in each bridges/*/ file
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `assetId`, `routeConfig` (`createInternalTransferRoute()`), `destinationAddress`
- Exploit idea: `IntentsBridge` emits `transfer` to any `receiver_id` with no asset checks. Token specifics: HOT ERC-20 on Polygon (USDC.e).
- Invariant to test: The bridge contract and chain named by the produced intent must equal the custodian of `nep245:v2_1.omni.hot.tg:137_2791bca1f2de4661ed88a30c99a7a9449aa84174` and the chain the caller named; a mismatch must throw, never fall through to the next bridge.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: construct IntentsSDK with mocked RPC/HTTP, call `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` with `nep245:v2_1.omni.hot.tg:137_2791bca1f2de4661ed88a30c99a7a9449aa84174` and `createInternalTransferRoute()`, assert `bridge.route` and the intent's `receiver_id`/`recipient`/chain.
