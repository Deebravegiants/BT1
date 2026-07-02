# Q2185: getRsETHAmountToMint Asset Identity Confusion Oracle rsETH P2185

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: rsETH transfer route; amount case 1 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 1 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the asset identity confusion path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: rsETH transfer route; amount case 1 ether; timing one second before daily reset; caller model EOA caller.
