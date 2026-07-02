# Q1498: receiveFromLRTConverter Supply Zero Transition Converter Desync daily P1498

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to protocol insolvency? Probe condition: daily fee mint limit route; amount case daily limit exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: daily fee mint limit route; amount case daily limit exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the supply-zero transition path against receiveFromLRTConverter and look for converter desync breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: daily fee mint limit route; amount case daily limit exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
