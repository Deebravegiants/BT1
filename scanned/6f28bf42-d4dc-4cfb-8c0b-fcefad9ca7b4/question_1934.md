# Q1934: getRsETHAmountToMint Round Down Accumulation Oracle deposit-limit P1934

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: deposit-limit accounting route; amount case available liquidity exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case available liquidity exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the round-down accumulation path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: deposit-limit accounting route; amount case available liquidity exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
