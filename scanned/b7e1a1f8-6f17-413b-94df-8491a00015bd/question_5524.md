# Q5524: Aptos all-zero address via OmniBridge (processWithdrawal)

## Question
Using `IntentsSDK.processWithdrawal` for `Aptos`, can `0x0000000000000000000000000000000000000000000000000000000000000000` (all-zero address) pass `validateAptosAddress` and reach `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` so that the destination on chain is not the one validated, given that not in any reject list; burn address on Aptos?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateAptosAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`0x0000000000000000000000000000000000000000000000000000000000000000`), `assetId` for a Aptos omni token, `destinationMemo`
- Exploit idea: not in any reject list; burn address on Aptos. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'aptos:mainnet')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x0000000000000000000000000000000000000000000000000000000000000000` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x0000000000000000000000000000000000000000000000000000000000000000', Chains.Aptos)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
