# Q2582: getAssetCurrentLimit Min Amount Bypass Deposit Limit stETH P2582

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: stETH supported asset route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the min-amount bypass path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: stETH supported asset route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.
