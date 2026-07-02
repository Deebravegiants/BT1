# Q2588: getAssetCurrentLimit Min Amount Bypass Distribution Loop LRTConverter P2588

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the min-amount bypass path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.
