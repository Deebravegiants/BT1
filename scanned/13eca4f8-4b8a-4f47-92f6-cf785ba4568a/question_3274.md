# Q3274: getETHDistributionData Buffer Under Reservation Donation Accounting deposit-limit P3274

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: deposit-limit accounting route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: deposit-limit accounting route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the buffer under-reservation path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: deposit-limit accounting route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller.
