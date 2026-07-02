# Q3171: getETHDistributionData Pause Boundary Race Converter Desync EigenLayer P3171

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: race a public action around a pause or public price-triggered pause transition; validation style: a helper contract batching allowed public calls; probe condition: EigenLayer queued-withdrawal route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the pause boundary race path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: EigenLayer queued-withdrawal route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller.
