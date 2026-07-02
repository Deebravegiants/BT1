# Q2339: getAssetCurrentLimit Round Up Insolvency Deposit Limit Lido P2339

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the round-up insolvency path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.
