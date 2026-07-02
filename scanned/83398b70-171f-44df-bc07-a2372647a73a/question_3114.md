# Q3114: getETHDistributionData Zero Or Dust Edge eth Accounting deposit-limit P3114

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the zero-or-dust edge path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller.
