# Q3359: getETHDistributionData Min Amount Bypass Donation Accounting Lido P3359

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 0.01 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 0.01 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the min-amount bypass path against getETHDistributionData and look for donation accounting breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: Lido stETH unstake route; amount case 0.01 ether; timing immediately after reward sendFunds; caller model EOA caller.
