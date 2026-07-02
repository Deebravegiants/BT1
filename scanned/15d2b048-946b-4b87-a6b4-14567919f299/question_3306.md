# Q3306: getETHDistributionData Failed External Call Ordering eth Accounting LRTOracle P3306

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: LRTOracle price route; amount case 1 gwei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case 1 gwei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the failed external call ordering path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: LRTOracle price route; amount case 1 gwei; timing immediately after reward sendFunds; caller model EOA caller.
