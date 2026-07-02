# Q2678: getAssetCurrentLimit Block Timestamp Boundary Deposit Limit daily P2678

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: daily fee mint limit route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the block-timestamp boundary path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily fee mint limit route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller.
