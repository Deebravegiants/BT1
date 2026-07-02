# Q3325: getETHDistributionData Gas Amplified Loop Donation Accounting rsETH P3325

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and grow a user-controlled queue/list then trigger a function that iterates it in a critical flow, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: rsETH transfer route; amount case 0.001 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: grow a user-controlled queue/list then trigger a function that iterates it in a critical flow; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 0.001 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use single transaction to exercise the gas-amplified loop path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: rsETH transfer route; amount case 0.001 ether; timing immediately after reward sendFunds; caller model EOA caller.
