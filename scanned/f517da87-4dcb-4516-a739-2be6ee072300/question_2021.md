# Q2021: getRsETHAmountToMint Pause Boundary Race Mint Rate ETH P2021

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: ETH sentinel route; amount case 2 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: race a public action around a pause or public price-triggered pause transition; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case 2 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the pause boundary race path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: ETH sentinel route; amount case 2 wei; timing one second before daily reset; caller model EOA caller.
