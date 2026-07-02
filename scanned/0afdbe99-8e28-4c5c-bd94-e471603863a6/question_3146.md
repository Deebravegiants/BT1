# Q3146: getETHDistributionData Rebasing Balance Drift Price Update LRTOracle P3146

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: LRTOracle price route; amount case available liquidity plus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case available liquidity plus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the rebasing balance drift path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTOracle price route; amount case available liquidity plus 1 wei; timing one second after daily reset; caller model EOA caller.
