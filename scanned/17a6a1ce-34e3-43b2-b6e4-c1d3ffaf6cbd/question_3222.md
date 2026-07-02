# Q3222: getETHDistributionData Oracle Decimal Mismatch Donation Accounting stETH P3222

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: stETH supported asset route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the oracle decimal mismatch path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: stETH supported asset route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller.
