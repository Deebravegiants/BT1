# Q4952: Tron hex address with 0x prefix via PoaBridge (createWithdrawalIntents)

## Question
Using `IntentsSDK.createWithdrawalIntents` for `Tron`, can `0x41a614f803b6fd780986a42c78ec9c7f77e6ded13c` (hex address with 0x prefix) pass `validateTronAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that `hex.decode` on a 0x-prefixed string throws -> false; but `compareAddresses` also returns false on throw, so token-address block is skipped?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateTronAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`0x41a614f803b6fd780986a42c78ec9c7f77e6ded13c`), `assetId` for a Tron poa token, `destinationMemo`
- Exploit idea: `hex.decode` on a 0x-prefixed string throws -> false; but `compareAddresses` also returns false on throw, so token-address block is skipped. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'tron:27Lqcw')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x41a614f803b6fd780986a42c78ec9c7f77e6ded13c` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x41a614f803b6fd780986a42c78ec9c7f77e6ded13c', Chains.Tron)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
