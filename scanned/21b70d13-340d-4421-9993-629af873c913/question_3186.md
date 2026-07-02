# Q3186: getETHDistributionData Queue Head Blocking Converter Desync LRTOracle P3186

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and place a pathological first queue item that blocks later honest requests from completing, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that one request cannot permanently or temporarily freeze unrelated user funds; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: LRTOracle price route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: place a pathological first queue item that blocks later honest requests from completing; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the queue head blocking path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: one request cannot permanently or temporarily freeze unrelated user funds; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: LRTOracle price route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller.
