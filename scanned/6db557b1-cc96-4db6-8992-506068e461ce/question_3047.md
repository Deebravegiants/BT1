# Q3047: Base all-lowercase address via OmniBridge (estimateWithdrawalFee)

## Question
Can an unprivileged user enter through `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` on the OmniBridge route for Base with `destinationAddress` = `0xdac17f958d2ee523a2206206994597c13d831ec7` (all-lowercase address) and make `validateAddress` (`validateEthAddress`) accept a string that `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` then forwards unchanged, so the address the Omni Bridge connector on the destination chain pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`0xdac17f958d2ee523a2206206994597c13d831ec7`), `assetId` for a Base omni token, `destinationMemo`
- Exploit idea: strict mode accepts all-lowercase; `compareAddresses` uses `getAddress` so token-address block works, but the memo/recipient is lowercase. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:8453')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0xdac17f958d2ee523a2206206994597c13d831ec7` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0xdac17f958d2ee523a2206206994597c13d831ec7', Chains.Base)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
