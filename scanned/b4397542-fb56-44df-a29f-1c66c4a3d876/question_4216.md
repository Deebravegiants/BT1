# Q4216: EVM target Arbitrum an EOA in all-lowercase (str via OmniBridge

## Question
On Arbitrum via OmniBridge, `validateEthAddress` rejects only the zero address and `0x…dead`. Can an unprivileged user set `destinationAddress` to an EOA in all-lowercase (strict isAddress accepts) (`0xaf88d065e77c8cc2239327c5edb3a432268e5831`) so that `compareAddresses` does not block it (it only compares against the bridged token's own address), the intent is signed, and the Omni Bridge connector on the destination chain delivers native or ERC-20 value into a contract that cannot forward it, with no path back to the user?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; compareAddresses.ts; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `0xaf88d065e77c8cc2239327c5edb3a432268e5831`
- Exploit idea: Reject list is two addresses; token-address block covers one contract. Native withdrawals to non-payable contracts revert at the bridge or burn.
- Invariant to test: destination is an account able to receive the asset type being withdrawn on that chain.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert acceptance; document bridge behaviour for contract recipients.
