# Q2216: getRsETHAmountToMint Allowance Race Stale Price queued P2216

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: queued buffer route; amount case 31.999999 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case 31.999999 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the allowance race path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: queued buffer route; amount case 31.999999 ether; timing one second before daily reset; caller model EOA caller.
