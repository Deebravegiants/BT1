# Q2283: getRsETHAmountToMint Unclaimed Yield Diversion Mint Rate ETHx P2283

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: ETHx supported asset route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: a helper contract batching allowed public calls; probe condition: ETHx supported asset route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the unclaimed-yield diversion path against getRsETHAmountToMint and look for mint rate breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: ETHx supported asset route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.
