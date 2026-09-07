# Q2062: Polygon all-lowercase address via OmniBridge (createWithdrawalIntents)

## Question
If a counterparty supplies `destinationAddress` = `0xdac17f958d2ee523a2206206994597c13d831ec7` (all-lowercase address) for a Polygon withdrawal via `IntentsSDK.createWithdrawalIntents`, does `validateEthAddress` return true while `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` encodes a value the Omni Bridge connector on the destination chain interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`0xdac17f958d2ee523a2206206994597c13d831ec7`), `assetId` for a Polygon omni token, `destinationMemo`
- Exploit idea: strict mode accepts all-lowercase; `compareAddresses` uses `getAddress` so token-address block works, but the memo/recipient is lowercase. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:137')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0xdac17f958d2ee523a2206206994597c13d831ec7` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0xdac17f958d2ee523a2206206994597c13d831ec7', Chains.Polygon)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
