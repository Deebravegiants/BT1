# Q2641: getAssetCurrentLimit Supply Zero Transition Deposit Limit ETH P2641

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: ETH sentinel route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the supply-zero transition path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: ETH sentinel route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.
