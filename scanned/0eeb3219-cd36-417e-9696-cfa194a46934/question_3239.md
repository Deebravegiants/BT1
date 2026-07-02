# Q3239: getETHDistributionData Highest Price Ratchet Price Update Lido P3239

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: Lido stETH unstake route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the highest-price ratchet path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Lido stETH unstake route; amount case 2 wei; timing immediately after reward sendFunds; caller model EOA caller.
