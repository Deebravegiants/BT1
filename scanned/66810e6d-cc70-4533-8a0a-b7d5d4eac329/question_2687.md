# Q2687: getAssetCurrentLimit Block Timestamp Boundary Rounding FeeReceiver P2687

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: FeeReceiver reward route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: a local supported-token harness with configurable transfer behavior; probe condition: FeeReceiver reward route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the block-timestamp boundary path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: FeeReceiver reward route; amount case daily limit exactly; timing exactly at daily reset; caller model EOA caller.
