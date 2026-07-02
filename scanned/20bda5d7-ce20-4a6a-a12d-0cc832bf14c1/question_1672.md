# Q1672: receiveFromNodeDelegator FirstExcludedIndex Boundary Deposit Limit Aave P1672

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: Aave aWETH liquidity route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: a fork test using current deployed balances and supported assets; probe condition: Aave aWETH liquidity route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the firstExcludedIndex boundary path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Aave aWETH liquidity route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
