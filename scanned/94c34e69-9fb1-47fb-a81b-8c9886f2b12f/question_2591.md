# Q2591: getAssetCurrentLimit Min Amount Bypass Rounding EigenLayer P2591

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: EigenLayer queued-withdrawal route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: a local supported-token harness with configurable transfer behavior; probe condition: EigenLayer queued-withdrawal route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the min-amount bypass path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: EigenLayer queued-withdrawal route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.
