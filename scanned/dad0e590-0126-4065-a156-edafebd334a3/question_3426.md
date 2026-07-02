# Q3426: getETHDistributionData Committed Assets Desync Converter Desync LRTOracle P3426

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: LRTOracle price route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the committed-assets desync path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: LRTOracle price route; amount case 32 ether; timing immediately after reward sendFunds; caller model EOA caller.
