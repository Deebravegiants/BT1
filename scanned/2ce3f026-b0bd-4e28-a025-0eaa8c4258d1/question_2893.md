# Q2893: getAssetDistributionData Buffer Over Reservation Gas Growth Merkle-free P2893

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, gas growth must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to unbounded gas consumption? Probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the buffer over-reservation path against getAssetDistributionData and look for gas growth breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, gas growth must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Unbounded gas consumption
- Fast validation: grow attacker-controlled queues/arrays and measure whether settlement exceeds block gas limits Use probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing one second after daily reset; caller model EOA caller.
