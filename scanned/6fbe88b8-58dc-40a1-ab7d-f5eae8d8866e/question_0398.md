# Q0398: BitcoinCash legacy 1... address with wrong checksum via PoaBridge (processWithdrawal)

## Question
Using `IntentsSDK.processWithdrawal` for `BitcoinCash`, can `1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN3` (legacy 1... address with wrong checksum) pass `validateBchAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that legacy branch is a regex only (`/^1[1-9A-HJ-NP-Za-km-z]{25,34}$/`), no Base58Check verification?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBchAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN3`), `assetId` for a BitcoinCash poa token, `destinationMemo`
- Exploit idea: legacy branch is a regex only (`/^1[1-9A-HJ-NP-Za-km-z]{25,34}$/`), no Base58Check verification. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000000000000651ef99cb9fcbe')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN3` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN3', Chains.BitcoinCash)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
