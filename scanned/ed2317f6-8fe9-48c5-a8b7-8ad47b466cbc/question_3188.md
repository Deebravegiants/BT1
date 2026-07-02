# Q3188: getETHDistributionData Queue Head Blocking eth Accounting LRTConverter P3188

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and place a pathological first queue item that blocks later honest requests from completing, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that one request cannot permanently or temporarily freeze unrelated user funds; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: place a pathological first queue item that blocks later honest requests from completing; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the queue head blocking path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: one request cannot permanently or temporarily freeze unrelated user funds; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: LRTConverter ETH-in-withdrawal route; amount case deposit limit plus 1 wei; timing one second after daily reset; caller model EOA caller.
