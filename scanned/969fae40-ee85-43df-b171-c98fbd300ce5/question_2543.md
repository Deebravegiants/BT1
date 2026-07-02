# Q2543: getAssetCurrentLimit Failed External Call Ordering Rounding ETHx P2543

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: ETHx supported asset route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the failed external call ordering path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETHx supported asset route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller.
