# Q2585: getAssetCurrentLimit Min Amount Bypass Distribution Loop rsETH P2585

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: rsETH transfer route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: several attacker accounts creating adjacent requests; probe condition: rsETH transfer route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the min-amount bypass path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: rsETH transfer route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.
