# Q2408: getAssetCurrentLimit Pause Boundary Race Distribution Loop LRTConverter P2408

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: race a public action around a pause or public price-triggered pause transition; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the pause boundary race path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 wei; timing exactly at daily reset; caller model EOA caller.
