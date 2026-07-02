# Q1165: receiveFromLRTConverter Round Down Accumulation Converter Desync rsETH P1165

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to protocol insolvency? Probe condition: rsETH transfer route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the round-down accumulation path against receiveFromLRTConverter and look for converter desync breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: rsETH transfer route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
