# Q3210: getETHDistributionData FirstExcludedIndex Boundary eth Accounting NodeDelegator P3210

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: NodeDelegator pod-share route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the firstExcludedIndex boundary path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: NodeDelegator pod-share route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
