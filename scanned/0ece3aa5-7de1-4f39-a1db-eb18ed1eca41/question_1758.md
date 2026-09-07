# Q1758: BNB an address that is a contract without receive() via OmniBridge (processWithdrawal)

## Question
Using `IntentsSDK.processWithdrawal` for `BNB`, can `0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984` (an address that is a contract without receive()) pass `validateEthAddress` and reach `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` so that the destination on chain is not the one validated, given that format-only validation; native withdrawals to non-payable contracts revert on destination and may strand funds at the bridge?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984`), `assetId` for a BNB omni token, `destinationMemo`
- Exploit idea: format-only validation; native withdrawals to non-payable contracts revert on destination and may strand funds at the bridge. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:56')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984', Chains.BNB)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
