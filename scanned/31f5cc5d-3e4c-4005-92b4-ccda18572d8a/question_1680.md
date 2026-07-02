# Q1680: receiveFromNodeDelegator FirstExcludedIndex Boundary Deposit Limit Swell P1680

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the firstExcludedIndex boundary path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Swell swETH legacy route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
