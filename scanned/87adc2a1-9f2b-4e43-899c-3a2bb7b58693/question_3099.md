# Q3099: getETHDistributionData Round Up Insolvency eth Accounting Lido P3099

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: Lido stETH unstake route; amount case daily limit exactly; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case daily limit exactly; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the round-up insolvency path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: Lido stETH unstake route; amount case daily limit exactly; timing one second after daily reset; caller model EOA caller.
