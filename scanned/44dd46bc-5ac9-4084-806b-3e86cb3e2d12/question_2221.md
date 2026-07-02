# Q2221: getRsETHAmountToMint Cross Contract Stale Read Rounding ETH P2221

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and make one contract read another contract before its state reflects a prior step in the same attack sequence, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case 32 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: make one contract read another contract before its state reflects a prior step in the same attack sequence; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case 32 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the cross-contract stale read path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETH sentinel route; amount case 32 ether; timing one second before daily reset; caller model EOA caller.
