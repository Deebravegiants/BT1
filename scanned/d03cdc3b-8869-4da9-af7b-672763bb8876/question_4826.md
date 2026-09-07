# Q4826: Solana 31-byte base58 string via OmniBridge (createWithdrawalIntents)

## Question
If a counterparty supplies `destinationAddress` = `3fWfHb3QXRfibFQCUjzXd5g7Be7bfhvg9gJ1dRnPzdF` (31-byte base58 string) for a Solana withdrawal via `IntentsSDK.createWithdrawalIntents`, does `validateSolAddress` return true while `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` encodes a value the Omni Bridge connector on the destination chain interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateSolAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`3fWfHb3QXRfibFQCUjzXd5g7Be7bfhvg9gJ1dRnPzdF`), `assetId` for a Solana omni token, `destinationMemo`
- Exploit idea: length check is 32 bytes exactly; confirm no leading-zero normalisation. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `3fWfHb3QXRfibFQCUjzXd5g7Be7bfhvg9gJ1dRnPzdF` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('3fWfHb3QXRfibFQCUjzXd5g7Be7bfhvg9gJ1dRnPzdF', Chains.Solana)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
