# Q2401: getAssetCurrentLimit Pause Boundary Race Deposit Limit ETH P2401

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: ETH sentinel route; amount case 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: race a public action around a pause or public price-triggered pause transition; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the pause boundary race path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: ETH sentinel route; amount case 1 wei; timing exactly at daily reset; caller model EOA caller.
