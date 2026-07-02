# Q3419: getETHDistributionData Supply Zero Transition Converter Desync Lido P3419

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the supply-zero transition path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller.
