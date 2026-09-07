# Q3307: Memo TON: a `destinationMemo` on a HOT TON withdra (signAndSendWithdrawalIntent)

## Question
Via `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` for TON, can an unprivileged user supply a `destinationMemo` on a HOT TON withdrawal to an exchange deposit address so that the memo/tag encoded by the bridge adapter (HOT does not support memos; funds land without the exchange's required comment) causes the destination to receive funds it cannot attribute (exchange deposit lost) or the relayer to pay a different tag/account than validated?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts `createWithdrawMemo`; poa-bridge.ts `validateWithdrawal` (XRPL branch); hot-bridge.ts `createWithdrawalIntents`; intents-bridge.ts
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationMemo`, `destinationAddress`
- Exploit idea: HOT does not support memos; funds land without the exchange's required comment
- Invariant to test: the memo/tag delivered on chain == the memo/tag the user passed, and a memo is only accepted for chains where the bridge honours it.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: build intents with the memo and inspect the emitted memo/msg string; compare with the bridge's parser rules.
