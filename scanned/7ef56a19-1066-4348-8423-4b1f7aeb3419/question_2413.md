# Q2413: getAssetCurrentLimit Queue Head Blocking Rounding Merkle-free P2413

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and place a pathological first queue item that blocks later honest requests from completing, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that one request cannot permanently or temporarily freeze unrelated user funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: Merkle-free yield accounting route; amount case 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: place a pathological first queue item that blocks later honest requests from completing; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the queue head blocking path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: one request cannot permanently or temporarily freeze unrelated user funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Merkle-free yield accounting route; amount case 1 wei; timing exactly at daily reset; caller model EOA caller.
