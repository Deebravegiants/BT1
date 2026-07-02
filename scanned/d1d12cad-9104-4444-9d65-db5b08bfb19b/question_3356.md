# Q3356: getETHDistributionData Min Amount Bypass Converter Desync queued P3356

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: queued buffer route; amount case 0.01 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case 0.01 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the min-amount bypass path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: queued buffer route; amount case 0.01 ether; timing immediately after reward sendFunds; caller model EOA caller.
