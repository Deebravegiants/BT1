# Q3242: getETHDistributionData Fee Mint Limit Boundary Price Update stETH P3242

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: stETH supported asset route; amount case minAmount minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case minAmount minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the fee mint limit boundary path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: stETH supported asset route; amount case minAmount minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
