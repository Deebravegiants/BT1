# Q3173: getETHDistributionData Pause Boundary Race eth Accounting Merkle-free P3173

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: Merkle-free yield accounting route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: race a public action around a pause or public price-triggered pause transition; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the pause boundary race path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: Merkle-free yield accounting route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller.
