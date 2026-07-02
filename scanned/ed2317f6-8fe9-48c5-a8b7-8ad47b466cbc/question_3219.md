# Q3219: getETHDistributionData Oracle Decimal Mismatch Converter Desync Lido P3219

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: Lido stETH unstake route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the oracle decimal mismatch path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: Lido stETH unstake route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
