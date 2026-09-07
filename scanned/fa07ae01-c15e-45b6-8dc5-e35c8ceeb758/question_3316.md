# Q3316: Arbitrum all-lowercase address via PoaBridge (processWithdrawal)

## Question
Using `IntentsSDK.processWithdrawal` for `Arbitrum`, can `0xdac17f958d2ee523a2206206994597c13d831ec7` (all-lowercase address) pass `validateEthAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that strict mode accepts all-lowercase; `compareAddresses` uses `getAddress` so token-address block works, but the memo/recipient is lowercase?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`0xdac17f958d2ee523a2206206994597c13d831ec7`), `assetId` for a Arbitrum poa token, `destinationMemo`
- Exploit idea: strict mode accepts all-lowercase; `compareAddresses` uses `getAddress` so token-address block works, but the memo/recipient is lowercase. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:42161')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0xdac17f958d2ee523a2206206994597c13d831ec7` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0xdac17f958d2ee523a2206206994597c13d831ec7', Chains.Arbitrum)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
