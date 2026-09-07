# Q2628: Memo Stellar: a `destinationMemo` on a HOT Stellar wit (processWithdrawal)

## Question
Via `IntentsSDK.processWithdrawal` for Stellar, can an unprivileged user supply a `destinationMemo` on a HOT Stellar withdrawal so that the memo/tag encoded by the bridge adapter (`UnsupportedDestinationMemoError` thrown only in `createWithdrawalIntents`, not in `validateWithdrawal`/estimate) causes the destination to receive funds it cannot attribute (exchange deposit lost) or the relayer to pay a different tag/account than validated?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts `createWithdrawMemo`; poa-bridge.ts `validateWithdrawal` (XRPL branch); hot-bridge.ts `createWithdrawalIntents`; intents-bridge.ts
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationMemo`, `destinationAddress`
- Exploit idea: `UnsupportedDestinationMemoError` thrown only in `createWithdrawalIntents`, not in `validateWithdrawal`/estimate
- Invariant to test: the memo/tag delivered on chain == the memo/tag the user passed, and a memo is only accepted for chains where the bridge honours it.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: build intents with the memo and inspect the emitted memo/msg string; compare with the bridge's parser rules.
