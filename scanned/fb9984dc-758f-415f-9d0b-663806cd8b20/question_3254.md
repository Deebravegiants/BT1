# Q3254: getETHDistributionData Aave Liquidity Shortfall eth Accounting deposit-limit P3254

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: deposit-limit accounting route; amount case minAmount minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case minAmount minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the Aave liquidity shortfall path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: deposit-limit accounting route; amount case minAmount minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
