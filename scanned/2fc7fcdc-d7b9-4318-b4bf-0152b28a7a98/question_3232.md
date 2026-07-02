# Q3232: getETHDistributionData Highest Price Ratchet eth Accounting Aave P3232

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: Aave aWETH liquidity route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: a fork test using current deployed balances and supported assets; probe condition: Aave aWETH liquidity route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the highest-price ratchet path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: Aave aWETH liquidity route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller.
