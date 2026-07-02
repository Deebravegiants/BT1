# Q3101: getETHDistributionData Round Up Insolvency Converter Desync ETH P3101

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: ETH sentinel route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the round-up insolvency path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: ETH sentinel route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller.
