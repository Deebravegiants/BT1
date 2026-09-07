# Q4701: HyperEvm an address that is a contract without receive() via OmniBridge (estimateWithdrawalFee)

## Question
If a counterparty supplies `destinationAddress` = `0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984` (an address that is a contract without receive()) for a HyperEvm withdrawal via `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false`, does `validateEthAddress` return true while `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` encodes a value the Omni Bridge connector on the destination chain interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984`), `assetId` for a HyperEvm omni token, `destinationMemo`
- Exploit idea: format-only validation; native withdrawals to non-payable contracts revert on destination and may strand funds at the bridge. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:999')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984', Chains.HyperEvm)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
