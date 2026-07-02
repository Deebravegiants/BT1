# Q3305: getETHDistributionData Failed External Call Ordering Price Update rsETH P3305

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH transfer route; amount case 1 gwei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: several attacker accounts creating adjacent requests; probe condition: rsETH transfer route; amount case 1 gwei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the failed external call ordering path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: rsETH transfer route; amount case 1 gwei; timing immediately after reward sendFunds; caller model EOA caller.
