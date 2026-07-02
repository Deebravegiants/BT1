# Q3230: getETHDistributionData Highest Price Ratchet Converter Desync NodeDelegator P3230

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: NodeDelegator pod-share route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: two transactions before and after updateRSETHPrice; probe condition: NodeDelegator pod-share route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the highest-price ratchet path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: NodeDelegator pod-share route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller.
