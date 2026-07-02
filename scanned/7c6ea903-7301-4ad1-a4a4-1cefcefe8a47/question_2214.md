# Q2214: getRsETHAmountToMint Allowance Race Rounding deposit-limit P2214

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: deposit-limit accounting route; amount case 31.999999 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case 31.999999 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the allowance race path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: deposit-limit accounting route; amount case 31.999999 ether; timing one second before daily reset; caller model EOA caller.
