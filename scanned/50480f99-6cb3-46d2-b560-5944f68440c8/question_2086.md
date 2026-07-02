# Q2086: getRsETHAmountToMint Highest Price Ratchet Oracle LRTOracle P2086

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the highest-price ratchet path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller.
