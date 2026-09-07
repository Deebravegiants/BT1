# Q3983: Memo Near: `destinationMemo` on an IntentsBridge in (createWithdrawalIntents)

## Question
Via `IntentsSDK.createWithdrawalIntents` for Near, can an unprivileged user supply `destinationMemo` on an IntentsBridge internal transfer to a contract account so that the memo/tag encoded by the bridge adapter (memo forwarded verbatim into `transfer.memo`) causes the destination to receive funds it cannot attribute (exchange deposit lost) or the relayer to pay a different tag/account than validated?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts `createWithdrawMemo`; poa-bridge.ts `validateWithdrawal` (XRPL branch); hot-bridge.ts `createWithdrawalIntents`; intents-bridge.ts
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationMemo`, `destinationAddress`
- Exploit idea: memo forwarded verbatim into `transfer.memo`
- Invariant to test: the memo/tag delivered on chain == the memo/tag the user passed, and a memo is only accepted for chains where the bridge honours it.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: build intents with the memo and inspect the emitted memo/msg string; compare with the bridge's parser rules.
