# Q0066: Bitcoin mixed-case bech32 via PoaBridge (processWithdrawal)

## Question
If a counterparty supplies `destinationAddress` = `bc1QAR0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq` (mixed-case bech32) for a Bitcoin withdrawal via `IntentsSDK.processWithdrawal`, does `validateBtcAddress` return true while `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` encodes a value the PoA bridge relayer (bridge.chaindefuser.com) interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBtcAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`bc1QAR0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq`), `assetId` for a Bitcoin poa token, `destinationMemo`
- Exploit idea: bech32 rejects mixed case but the try/catch falls through to bech32m and then to false; confirm no path returns true. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000019d6689c085ae165831e93')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `bc1QAR0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('bc1QAR0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq', Chains.Bitcoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
