# Q2117: HOT fee Monad an ERC-20/jett (`blockNumber` from a stale est)

## Question
On HOT bridge for Monad withdrawing an ERC-20/jetton (fee swapped via token_diff), when `blockNumber` from a stale estimate is reused for a new withdrawal, does `HotBridge.createWithdrawalIntents` compute `amount = withdrawalParams.amount + (isNative ? feeAmount : 0n)` and also push a `token_diff` from `feeEstimation.quote`, so the user pays the fee twice (once inside `mt_withdraw` amounts[1] / amount and once via the swap) or `buildGaslessWithdrawIntent` receives a `feeAmount` that does not match the quoted `amount_out`?

## Target
- File/function: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `createWithdrawalIntents`, `estimateWithdrawalFee`; hot-bridge-utils.ts `getFeeAssetIdForChain`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` / `processWithdrawal` with reused or caller-built `feeEstimation`
- Attacker controls: `feeEstimation` object (quote, underlyingFees.relayerFee, blockNumber), `assetId` for Monad
- Exploit idea: The sanity `assert(intent.amounts[0] === amount)` only checks HOT SDK echoed the amount; nothing checks quote vs isNative consistency or that `feeAmount` equals `quote.amount_out`.
- Invariant to test: total user debit == amount + feeEstimation.amount, with the fee charged exactly once in exactly one asset.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: mock hotSdk.buildGaslessWithdrawIntent, pass a FeeEstimation with both quote and native path, sum debits.
