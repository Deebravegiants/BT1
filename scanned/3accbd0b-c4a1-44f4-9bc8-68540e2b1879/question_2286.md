# Q2286: getRsETHAmountToMint Unclaimed Yield Diversion Stale Price LRTOracle P2286

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: LRTOracle price route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the unclaimed-yield diversion path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: LRTOracle price route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.
