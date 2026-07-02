# Q3132: getETHDistributionData Direct ETH Donation Skew Price Update Aave P3132

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: Aave aWETH liquidity route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: attacker-created state followed by an honest operator action; probe condition: Aave aWETH liquidity route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the direct ETH donation skew path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Aave aWETH liquidity route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.
