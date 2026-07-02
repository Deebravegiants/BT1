# Q2082: getRsETHAmountToMint Highest Price Ratchet Oracle stETH P2082

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: stETH supported asset route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the highest-price ratchet path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: stETH supported asset route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller.
