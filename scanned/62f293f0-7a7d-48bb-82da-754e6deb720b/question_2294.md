# Q2294: getRsETHAmountToMint Block Timestamp Boundary Mint Rate deposit-limit P2294

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: deposit-limit accounting route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the block-timestamp boundary path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: deposit-limit accounting route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.
