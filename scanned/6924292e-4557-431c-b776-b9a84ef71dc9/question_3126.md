# Q3126: getETHDistributionData Direct ETH Donation Skew Donation Accounting LRTOracle P3126

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the direct ETH donation skew path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: LRTOracle price route; amount case available liquidity exactly; timing one second after daily reset; caller model EOA caller.
