# Q3218: getETHDistributionData Oracle Decimal Mismatch Donation Accounting daily P3218

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: daily fee mint limit route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the oracle decimal mismatch path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: daily fee mint limit route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
