# Q1286: receiveFromLRTConverter FirstExcludedIndex Boundary Donation Accounting LRTOracle P1286

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to permanent freezing of funds? Probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the firstExcludedIndex boundary path against receiveFromLRTConverter and look for donation accounting breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
