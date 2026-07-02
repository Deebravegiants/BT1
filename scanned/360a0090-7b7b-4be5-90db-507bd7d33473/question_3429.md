# Q3429: getETHDistributionData Committed Assets Desync Donation Accounting LRTUnstakingVault P3429

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: LRTUnstakingVault instant-liquidity route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: LRTUnstakingVault instant-liquidity route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the committed-assets desync path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: LRTUnstakingVault instant-liquidity route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.
