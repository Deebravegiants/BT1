# Q1199: receiveFromLRTConverter Zero Or Dust Edge Converter Desync Lido P1199

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the zero-or-dust edge path against receiveFromLRTConverter and look for converter desync breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: Lido stETH unstake route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
