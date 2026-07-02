# Q2210: getRsETHAmountToMint Allowance Race Rounding NodeDelegator P2210

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: NodeDelegator pod-share route; amount case 31.999999 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: two transactions before and after updateRSETHPrice; probe condition: NodeDelegator pod-share route; amount case 31.999999 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the allowance race path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: NodeDelegator pod-share route; amount case 31.999999 ether; timing one second before daily reset; caller model EOA caller.
