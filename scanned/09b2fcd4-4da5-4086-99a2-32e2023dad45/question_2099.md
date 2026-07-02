# Q2099: getRsETHAmountToMint Fee Mint Limit Boundary Mint Rate Lido P2099

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: Lido stETH unstake route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the fee mint limit boundary path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: Lido stETH unstake route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller.
