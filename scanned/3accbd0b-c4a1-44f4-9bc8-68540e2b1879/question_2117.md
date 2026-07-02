# Q2117: getRsETHAmountToMint Buffer Under Reservation Mint Rate daily P2117

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: daily mint limit route; amount case 1 gwei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case 1 gwei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the buffer under-reservation path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: daily mint limit route; amount case 1 gwei; timing one second before daily reset; caller model EOA caller.
