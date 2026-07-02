# Q2004: getRsETHAmountToMint Rebasing Balance Drift Rounding rsETH P2004

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH burn route; amount case 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the rebasing balance drift path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH burn route; amount case 1 wei; timing one second before daily reset; caller model EOA caller.
