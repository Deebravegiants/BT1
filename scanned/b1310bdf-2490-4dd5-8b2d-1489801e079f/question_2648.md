# Q2648: getAssetCurrentLimit Supply Zero Transition Distribution Loop LRTConverter P2648

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the supply-zero transition path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.
