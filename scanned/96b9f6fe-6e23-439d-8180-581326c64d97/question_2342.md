# Q2342: getAssetCurrentLimit Zero Or Dust Edge Deposit Limit stETH P2342

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: stETH supported asset route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the zero-or-dust edge path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: stETH supported asset route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller.
