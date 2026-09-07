# Q0684: Zcash unified address with unknown typecode outside must-understand range via OmniBridge (processWithdrawal)

## Question
If a counterparty supplies `destinationAddress` = `u1<ua-with-typecode-0x10>` (unified address with unknown typecode outside must-understand range) for a Zcash withdrawal via `IntentsSDK.processWithdrawal`, does `validateZcashAddress` return true while `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` encodes a value the Omni Bridge connector on the destination chain interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateZcashAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`u1<ua-with-typecode-0x10>`), `assetId` for a Zcash omni token, `destinationMemo`
- Exploit idea: unknown typecodes are tolerated; a UA with only unknown + P2PKH receiver passes. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:00040fe8ec8471911baa1db1266ea15d')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `u1<ua-with-typecode-0x10>` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('u1<ua-with-typecode-0x10>', Chains.Zcash)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
