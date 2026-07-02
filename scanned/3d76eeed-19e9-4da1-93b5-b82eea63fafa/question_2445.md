# Q2445: getAssetCurrentLimit FirstExcludedIndex Boundary Distribution Loop rsETH P2445

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: rsETH transfer route; amount case minAmount minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case minAmount minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the firstExcludedIndex boundary path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: rsETH transfer route; amount case minAmount minus 1 wei; timing exactly at daily reset; caller model EOA caller.
