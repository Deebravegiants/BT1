# Q4747: Solana off-curve PDA via OmniBridge (processWithdrawal)

## Question
Using `IntentsSDK.processWithdrawal` for `Solana`, can `9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin` (off-curve PDA) pass `validateSolAddress` and reach `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` so that the destination on chain is not the one validated, given that 32 bytes passes; ATA-less recipient for SPL tokens?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateSolAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin`), `assetId` for a Solana omni token, `destinationMemo`
- Exploit idea: 32 bytes passes; ATA-less recipient for SPL tokens. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin', Chains.Solana)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
