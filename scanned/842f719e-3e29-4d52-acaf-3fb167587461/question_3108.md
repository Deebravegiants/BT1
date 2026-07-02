# Q3108: getETHDistributionData Round Up Insolvency Donation Accounting LRTConverter P3108

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: attacker-created state followed by an honest operator action; probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the round-up insolvency path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity minus 1 wei; timing one second after daily reset; caller model EOA caller.
