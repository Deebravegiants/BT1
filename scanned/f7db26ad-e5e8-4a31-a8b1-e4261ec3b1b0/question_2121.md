# Q2121: Memo BitcoinCash: `bitcoincash:` prefix in mixed case `Bit (processWithdrawal)

## Question
Via `IntentsSDK.processWithdrawal` for BitcoinCash, can an unprivileged user supply `bitcoincash:` prefix in mixed case `BitcoinCash:qpm...` so that the memo/tag encoded by the bridge adapter (`startsWith('bitcoincash:')` after toLowerCase strips only if lowercase; the mixed-case original is sliced by length) causes the destination to receive funds it cannot attribute (exchange deposit lost) or the relayer to pay a different tag/account than validated?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts `createWithdrawMemo`; poa-bridge.ts `validateWithdrawal` (XRPL branch); hot-bridge.ts `createWithdrawalIntents`; intents-bridge.ts
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationMemo`, `destinationAddress`
- Exploit idea: `startsWith('bitcoincash:')` after toLowerCase strips only if lowercase; the mixed-case original is sliced by length
- Invariant to test: the memo/tag delivered on chain == the memo/tag the user passed, and a memo is only accepted for chains where the bridge honours it.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: build intents with the memo and inspect the emitted memo/msg string; compare with the bridge's parser rules.
