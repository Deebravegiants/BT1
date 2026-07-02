# Q2357: getAssetCurrentLimit Direct ETH Donation Skew Deposit Limit daily P2357

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: daily mint limit route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the direct ETH donation skew path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily mint limit route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller.
