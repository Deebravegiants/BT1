# Q3213: getETHDistributionData FirstExcludedIndex Boundary Price Update Merkle-free P3213

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: Merkle-free yield accounting route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: Merkle-free yield accounting route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the firstExcludedIndex boundary path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Merkle-free yield accounting route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
