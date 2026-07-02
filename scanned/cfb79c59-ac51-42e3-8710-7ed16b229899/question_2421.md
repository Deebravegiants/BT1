# Q2421: getAssetCurrentLimit Queue Head Blocking Rounding ETH P2421

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and place a pathological first queue item that blocks later honest requests from completing, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that one request cannot permanently or temporarily freeze unrelated user funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: place a pathological first queue item that blocks later honest requests from completing; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: ETH sentinel route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the queue head blocking path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: one request cannot permanently or temporarily freeze unrelated user funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETH sentinel route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.
