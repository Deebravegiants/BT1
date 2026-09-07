# Q5540: Aptos all-zero address via OmniBridge (createWithdrawalIntents)

## Question
If a counterparty supplies `destinationAddress` = `0x0000000000000000000000000000000000000000000000000000000000000000` (all-zero address) for a Aptos withdrawal via `IntentsSDK.createWithdrawalIntents`, does `validateAptosAddress` return true while `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` encodes a value the Omni Bridge connector on the destination chain interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateAptosAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`0x0000000000000000000000000000000000000000000000000000000000000000`), `assetId` for a Aptos omni token, `destinationMemo`
- Exploit idea: not in any reject list; burn address on Aptos. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'aptos:mainnet')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x0000000000000000000000000000000000000000000000000000000000000000` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x0000000000000000000000000000000000000000000000000000000000000000', Chains.Aptos)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
