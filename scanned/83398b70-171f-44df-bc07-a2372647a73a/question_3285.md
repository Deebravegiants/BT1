# Q3285: getETHDistributionData Buffer Over Reservation Donation Accounting rsETH P3285

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: rsETH transfer route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the buffer over-reservation path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: rsETH transfer route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
