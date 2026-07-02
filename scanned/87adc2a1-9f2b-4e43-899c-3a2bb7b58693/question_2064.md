# Q2064: getRsETHAmountToMint FirstExcludedIndex Boundary Oracle rsETH P2064

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: rsETH burn route; amount case exact minAmount; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case exact minAmount; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the firstExcludedIndex boundary path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: rsETH burn route; amount case exact minAmount; timing one second before daily reset; caller model EOA caller.
