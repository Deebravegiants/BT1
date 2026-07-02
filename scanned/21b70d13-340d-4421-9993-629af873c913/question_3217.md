# Q3217: getETHDistributionData Oracle Decimal Mismatch eth Accounting daily P3217

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: daily mint limit route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: one transaction using a contract wallet and controlled calldata; probe condition: daily mint limit route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use single transaction to exercise the oracle decimal mismatch path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: daily mint limit route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
