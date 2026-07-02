# Q3362: getETHDistributionData Allowance Race Donation Accounting stETH P3362

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: stETH supported asset route; amount case 0.1 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case 0.1 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the allowance race path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: stETH supported asset route; amount case 0.1 ether; timing immediately after reward sendFunds; caller model EOA caller.
