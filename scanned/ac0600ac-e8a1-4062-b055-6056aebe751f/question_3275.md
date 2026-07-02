# Q3275: getETHDistributionData Buffer Under Reservation Converter Desync withdrawal P3275

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: withdrawal request nonce route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the buffer under-reservation path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: withdrawal request nonce route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller.
