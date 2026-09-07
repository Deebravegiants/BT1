# Q4941: EVM target Plasma the chain's canonical USDC/U via PoaBridge

## Question
On Plasma via PoaBridge, `validateEthAddress` rejects only the zero address and `0x…dead`. Can an unprivileged user set `destinationAddress` to the chain's canonical USDC/USDT contract (`0xB8CE59FC3717ada4C02eaDF9682A9e934F625ebb`) so that `compareAddresses` does not block it (it only compares against the bridged token's own address), the intent is signed, and the PoA bridge relayer (bridge.chaindefuser.com) delivers native or ERC-20 value into a contract that cannot forward it, with no path back to the user?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; compareAddresses.ts; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` / `createWithdrawalIntents`
- Attacker controls: `destinationAddress` = `0xB8CE59FC3717ada4C02eaDF9682A9e934F625ebb`
- Exploit idea: Reject list is two addresses; token-address block covers one contract. Native withdrawals to non-payable contracts revert at the bridge or burn.
- Invariant to test: destination is an account able to receive the asset type being withdrawn on that chain.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: assert acceptance; document bridge behaviour for contract recipients.
