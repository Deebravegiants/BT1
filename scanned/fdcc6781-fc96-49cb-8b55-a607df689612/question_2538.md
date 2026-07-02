# Q2538: getAssetCurrentLimit Failed External Call Ordering Deposit Limit daily P2538

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: daily fee mint limit route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: compare many dust calls against one large call; probe condition: daily fee mint limit route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the failed external call ordering path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily fee mint limit route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller.
