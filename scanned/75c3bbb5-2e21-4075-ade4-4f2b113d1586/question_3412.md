# Q3412: getETHDistributionData Supply Zero Transition Price Update Aave P3412

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: Aave aWETH liquidity route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: a fork test using current deployed balances and supported assets; probe condition: Aave aWETH liquidity route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the supply-zero transition path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Aave aWETH liquidity route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller.
