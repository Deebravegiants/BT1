# Q3456: getETHDistributionData Block Timestamp Boundary Converter Desync queued P3456

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: queued buffer route; amount case 32.000001 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: attacker-created state followed by an honest operator action; probe condition: queued buffer route; amount case 32.000001 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the block-timestamp boundary path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: queued buffer route; amount case 32.000001 ether; timing immediately after reward sendFunds; caller model EOA caller.
