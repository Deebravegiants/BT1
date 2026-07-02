# Q1674: receiveFromNodeDelegator FirstExcludedIndex Boundary Donation Accounting deposit-limit P1674

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: deposit-limit accounting route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the firstExcludedIndex boundary path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: deposit-limit accounting route; amount case exact minAmount; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
