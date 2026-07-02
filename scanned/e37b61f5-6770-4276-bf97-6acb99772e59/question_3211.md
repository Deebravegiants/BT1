# Q3211: getETHDistributionData FirstExcludedIndex Boundary Donation Accounting EigenLayer P3211

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: EigenLayer queued-withdrawal route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: an attacker contract as msg.sender or recipient; probe condition: EigenLayer queued-withdrawal route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the firstExcludedIndex boundary path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: EigenLayer queued-withdrawal route; amount case 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
