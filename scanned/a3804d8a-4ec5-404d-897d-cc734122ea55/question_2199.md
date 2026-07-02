# Q2199: getRsETHAmountToMint Min Amount Bypass Rounding Lido P2199

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 1 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case 1 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the min-amount bypass path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Lido stETH unstake route; amount case 1 ether; timing one second before daily reset; caller model EOA caller.
