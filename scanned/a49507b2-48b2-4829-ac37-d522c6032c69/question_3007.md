# Q3007: Base all-lowercase address via PoaBridge (createWithdrawalIntents)

## Question
Can an unprivileged user enter through `IntentsSDK.createWithdrawalIntents` on the PoaBridge route for Base with `destinationAddress` = `0xdac17f958d2ee523a2206206994597c13d831ec7` (all-lowercase address) and make `validateAddress` (`validateEthAddress`) accept a string that `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` then forwards unchanged, so the address the PoA bridge relayer (bridge.chaindefuser.com) pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`0xdac17f958d2ee523a2206206994597c13d831ec7`), `assetId` for a Base poa token, `destinationMemo`
- Exploit idea: strict mode accepts all-lowercase; `compareAddresses` uses `getAddress` so token-address block works, but the memo/recipient is lowercase. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:8453')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0xdac17f958d2ee523a2206206994597c13d831ec7` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0xdac17f958d2ee523a2206206994597c13d831ec7', Chains.Base)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
