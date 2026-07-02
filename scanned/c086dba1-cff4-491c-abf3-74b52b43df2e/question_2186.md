# Q2186: getRsETHAmountToMint Asset Identity Confusion Stale Price LRTOracle P2186

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: LRTOracle price route; amount case 1 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case 1 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the asset identity confusion path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: LRTOracle price route; amount case 1 ether; timing one second before daily reset; caller model EOA caller.
