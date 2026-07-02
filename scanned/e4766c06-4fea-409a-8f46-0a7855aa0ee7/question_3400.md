# Q3400: getETHDistributionData Unexpected Receiver Revert Converter Desync Swell P3400

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case 1 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case 1 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the unexpected receiver revert path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: Swell swETH legacy route; amount case 1 ether; timing immediately after reward sendFunds; caller model EOA caller.
