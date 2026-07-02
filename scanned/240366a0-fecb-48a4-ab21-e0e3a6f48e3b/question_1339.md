# Q1339: receiveFromLRTConverter Aave Liquidity Shortfall Converter Desync Lido P1339

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 0.001 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 0.001 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the Aave liquidity shortfall path against receiveFromLRTConverter and look for converter desync breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: Lido stETH unstake route; amount case 0.001 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
