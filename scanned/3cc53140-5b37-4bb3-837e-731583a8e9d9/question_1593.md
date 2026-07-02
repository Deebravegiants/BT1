# Q1593: receiveFromNodeDelegator Direct ETH Donation Skew Donation Accounting Merkle-free P1593

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: Merkle-free yield accounting route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: Merkle-free yield accounting route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the direct ETH donation skew path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: Merkle-free yield accounting route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
