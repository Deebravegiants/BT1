# Q2305: getAssetCurrentLimit Stale Price Sandwich Deposit Limit rsETH P2305

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: rsETH transfer route; amount case available liquidity minus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case available liquidity minus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the stale-price sandwich path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: rsETH transfer route; amount case available liquidity minus 1 wei; timing one second before daily reset; caller model EOA caller.
