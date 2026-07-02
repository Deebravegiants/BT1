# Q3123: getETHDistributionData Direct ETH Donation Skew Converter Desync ETHx P3123

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: ETHx supported asset route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: a helper contract batching allowed public calls; probe condition: ETHx supported asset route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the direct ETH donation skew path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: ETHx supported asset route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.
