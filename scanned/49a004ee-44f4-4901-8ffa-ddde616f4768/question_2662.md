# Q2662: getAssetCurrentLimit Committed Assets Desync Distribution Loop stETH P2662

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: stETH supported asset route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: stETH supported asset route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the committed-assets desync path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: stETH supported asset route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller.
