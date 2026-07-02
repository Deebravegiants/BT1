# Q2284: getRsETHAmountToMint Unclaimed Yield Diversion Rounding rsETH P2284

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: rsETH burn route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the unclaimed-yield diversion path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH burn route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.
