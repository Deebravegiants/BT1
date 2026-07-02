# Q2159: getRsETHAmountToMint Failed External Call Ordering Rounding Lido P2159

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: Lido stETH unstake route; amount case 0.01 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 0.01 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the failed external call ordering path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Lido stETH unstake route; amount case 0.01 ether; timing one second before daily reset; caller model EOA caller.
