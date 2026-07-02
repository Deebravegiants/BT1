# Q3286: getETHDistributionData Buffer Over Reservation Converter Desync LRTOracle P3286

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to temporary freezing of funds? Probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the buffer over-reservation path against getETHDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
