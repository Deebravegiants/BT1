# Q2264: getRsETHAmountToMint Supply Zero Transition Stale Price rsETH P2264

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH burn route; amount case daily limit minus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case daily limit minus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the supply-zero transition path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: rsETH burn route; amount case daily limit minus 1 wei; timing one second before daily reset; caller model EOA caller.
