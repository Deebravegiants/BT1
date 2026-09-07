# Q1759: EVM target Polygon the chain's canonical USDC/U via HotBridge

## Question
On Polygon via HotBridge, `validateEthAddress` rejects only the zero address and `0x…dead`. Can an unprivileged user set `destinationAddress` to the chain's canonical USDC/USDT contract (`0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`) so that `compareAddresses` does not block it (it only compares against the bridged token's own address), the intent is signed, and the HOT Omni bridge relayer delivers native or ERC-20 value into a contract that cannot forward it, with no path back to the user?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; compareAddresses.ts; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`
- Exploit idea: Reject list is two addresses; token-address block covers one contract. Native withdrawals to non-payable contracts revert at the bridge or burn.
- Invariant to test: destination is an account able to receive the asset type being withdrawn on that chain.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert acceptance; document bridge behaviour for contract recipients.
