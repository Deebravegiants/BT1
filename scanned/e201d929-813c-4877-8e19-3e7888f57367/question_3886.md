# Q3886: EVM target Arbitrum the chain's canonical USDC/U via PoaBridge

## Question
On Arbitrum via PoaBridge, `validateEthAddress` rejects only the zero address and `0x…dead`. Can an unprivileged user set `destinationAddress` to the chain's canonical USDC/USDT contract (`0xaf88d065e77c8cC2239327C5EDb3A432268e5831`) so that `compareAddresses` does not block it (it only compares against the bridged token's own address), the intent is signed, and the PoA bridge relayer (bridge.chaindefuser.com) delivers native or ERC-20 value into a contract that cannot forward it, with no path back to the user?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; compareAddresses.ts; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `0xaf88d065e77c8cC2239327C5EDb3A432268e5831`
- Exploit idea: Reject list is two addresses; token-address block covers one contract. Native withdrawals to non-payable contracts revert at the bridge or burn.
- Invariant to test: destination is an account able to receive the asset type being withdrawn on that chain.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert acceptance; document bridge behaviour for contract recipients.
