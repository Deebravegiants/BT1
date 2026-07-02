# Q3414: getETHDistributionData Supply Zero Transition Donation Accounting deposit-limit P3414

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: deposit-limit accounting route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the supply-zero transition path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: deposit-limit accounting route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller.
