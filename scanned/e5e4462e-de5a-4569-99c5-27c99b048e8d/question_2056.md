# Q2056: getRsETHAmountToMint FirstExcludedIndex Boundary Oracle queued P2056

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: queued buffer route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the firstExcludedIndex boundary path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: queued buffer route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller.
