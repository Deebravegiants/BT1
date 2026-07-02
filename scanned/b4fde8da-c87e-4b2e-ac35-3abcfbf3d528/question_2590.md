# Q2590: getAssetCurrentLimit Min Amount Bypass Deposit Limit NodeDelegator P2590

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: NodeDelegator pod-share route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: NodeDelegator pod-share route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the min-amount bypass path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: NodeDelegator pod-share route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.
