# Q0764: Memo XRPL: `destinationMemo` = `'0'` for an account (signAndSendWithdrawalIntent)

## Question
Via `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` for XRPL, can an unprivileged user supply `destinationMemo` = `'0'` for an account requiring a tag so that the memo/tag encoded by the bridge adapter (`!args.destinationMemo` treats '0' as present; tag 0 semantics on XRPL) causes the destination to receive funds it cannot attribute (exchange deposit lost) or the relayer to pay a different tag/account than validated?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts `createWithdrawMemo`; poa-bridge.ts `validateWithdrawal` (XRPL branch); hot-bridge.ts `createWithdrawalIntents`; intents-bridge.ts
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationMemo`, `destinationAddress`
- Exploit idea: `!args.destinationMemo` treats '0' as present; tag 0 semantics on XRPL
- Invariant to test: the memo/tag delivered on chain == the memo/tag the user passed, and a memo is only accepted for chains where the bridge honours it.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: build intents with the memo and inspect the emitted memo/msg string; compare with the bridge's parser rules.
