# Q3129: getETHDistributionData Direct ETH Donation Skew eth Accounting LRTUnstakingVault P3129

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: LRTUnstakingVault instant-liquidity route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: LRTUnstakingVault instant-liquidity route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the direct ETH donation skew path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: LRTUnstakingVault instant-liquidity route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.
