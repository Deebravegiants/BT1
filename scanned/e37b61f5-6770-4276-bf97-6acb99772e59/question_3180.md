# Q3180: getETHDistributionData Pause Boundary Race Price Update Swell P3180

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to failure to deliver promised returns without principal loss? Probe condition: Swell swETH legacy route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: race a public action around a pause or public price-triggered pause transition; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the pause boundary race path against getETHDistributionData and look for price update breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, price update must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Swell swETH legacy route; amount case deposit limit minus 1 wei; timing one second after daily reset; caller model EOA caller.
