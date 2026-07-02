# Q2688: getAssetCurrentLimit Block Timestamp Boundary Distribution Loop LRTConverter P2688

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: attacker-created state followed by an honest operator action; probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the block-timestamp boundary path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller.
