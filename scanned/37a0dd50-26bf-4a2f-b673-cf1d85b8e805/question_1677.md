# Q1677: receiveFromNodeDelegator FirstExcludedIndex Boundary Withdrawal Liquidity daily P1677

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to failure to deliver promised returns without principal loss? Probe condition: daily mint limit route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the firstExcludedIndex boundary path against receiveFromNodeDelegator and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: daily mint limit route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
