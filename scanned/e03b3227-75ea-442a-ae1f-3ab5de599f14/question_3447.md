# Q3447: getETHDistributionData Block Timestamp Boundary Donation Accounting FeeReceiver P3447

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: FeeReceiver reward route; amount case 32.000001 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: a helper contract batching allowed public calls; probe condition: FeeReceiver reward route; amount case 32.000001 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the block-timestamp boundary path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: FeeReceiver reward route; amount case 32.000001 ether; timing immediately after reward sendFunds; caller model EOA caller.
