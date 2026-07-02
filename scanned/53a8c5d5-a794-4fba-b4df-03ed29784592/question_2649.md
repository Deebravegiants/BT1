# Q2649: getAssetCurrentLimit Supply Zero Transition Deposit Limit LRTUnstakingVault P2649

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: LRTUnstakingVault instant-liquidity route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: LRTUnstakingVault instant-liquidity route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the supply-zero transition path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: LRTUnstakingVault instant-liquidity route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.
