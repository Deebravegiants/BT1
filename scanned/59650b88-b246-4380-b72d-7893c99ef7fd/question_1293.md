# Q1293: receiveFromLRTConverter FirstExcludedIndex Boundary Withdrawal Liquidity Merkle-free P1293

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to failure to deliver promised returns without principal loss? Probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the firstExcludedIndex boundary path against receiveFromLRTConverter and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
