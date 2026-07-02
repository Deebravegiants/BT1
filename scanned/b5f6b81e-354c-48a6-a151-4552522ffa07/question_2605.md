# Q2605: getAssetCurrentLimit Cross Contract Stale Read Rounding rsETH P2605

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and make one contract read another contract before its state reflects a prior step in the same attack sequence, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: rsETH transfer route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: make one contract read another contract before its state reflects a prior step in the same attack sequence; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the cross-contract stale read path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH transfer route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller.
