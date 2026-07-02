# Q2070: getRsETHAmountToMint Oracle Decimal Mismatch Rounding NodeDelegator P2070

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: NodeDelegator pod-share route; amount case exact minAmount; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case exact minAmount; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the oracle decimal mismatch path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: NodeDelegator pod-share route; amount case exact minAmount; timing one second before daily reset; caller model EOA caller.
