# Q3117: getETHDistributionData Zero Or Dust Edge Price Update daily P3117

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: daily mint limit route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the zero-or-dust edge path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: daily mint limit route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller.
