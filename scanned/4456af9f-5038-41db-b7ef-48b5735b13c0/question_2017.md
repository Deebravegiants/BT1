# Q2017: getRsETHAmountToMint Pause Boundary Race Mint Rate daily P2017

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: daily mint limit route; amount case 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: race a public action around a pause or public price-triggered pause transition; validation style: one transaction using a contract wallet and controlled calldata; probe condition: daily mint limit route; amount case 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the pause boundary race path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: daily mint limit route; amount case 1 wei; timing one second before daily reset; caller model EOA caller.
