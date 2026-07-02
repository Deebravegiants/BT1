# Q3269: getETHDistributionData Buffer Under Reservation eth Accounting LRTUnstakingVault P3269

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: LRTUnstakingVault instant-liquidity route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: several attacker accounts creating adjacent requests; probe condition: LRTUnstakingVault instant-liquidity route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the buffer under-reservation path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: LRTUnstakingVault instant-liquidity route; amount case exact minAmount; timing immediately after reward sendFunds; caller model EOA caller.
