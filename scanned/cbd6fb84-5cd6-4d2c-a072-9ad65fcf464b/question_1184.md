# Q1184: receiveFromLRTConverter Round Up Insolvency Converter Desync rsETH P1184

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to protocol insolvency? Probe condition: rsETH burn route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the round-up insolvency path against receiveFromLRTConverter and look for converter desync breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: rsETH burn route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
