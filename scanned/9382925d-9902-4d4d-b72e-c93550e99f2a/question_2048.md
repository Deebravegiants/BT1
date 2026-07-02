# Q2048: getRsETHAmountToMint Nonce Collision Attempt Rounding LRTConverter P2048

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: LRTConverter ETH-in-withdrawal route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the nonce collision attempt path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: LRTConverter ETH-in-withdrawal route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller.
