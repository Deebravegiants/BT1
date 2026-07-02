# Q3406: getETHDistributionData Unexpected Receiver Revert eth Accounting LRTOracle P3406

## Question
Can an unprivileged ETH depositor or ETH sender enter through `depositETH and updateRSETHPrice indirectly read getETHDistributionData()` while controlling direct ETH sends, deposit size, and price-update ordering and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::getETHDistributionData` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData, leading to permanent freezing of funds? Probe condition: LRTOracle price route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getETHDistributionData
- Entrypoint: depositETH and updateRSETHPrice indirectly read getETHDistributionData()
- Attacker controls: direct ETH sends, deposit size, and price-update ordering; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: LRTOracle price route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the unexpected receiver revert path against getETHDistributionData and look for eth accounting breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, eth accounting must not violate backing, queue, yield, or liquidity accounting for getETHDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track raw ETH balances across pool, NDC, converter, vault, and oracle TVL reads Use probe condition: LRTOracle price route; amount case 31.999999 ether; timing immediately after reward sendFunds; caller model EOA caller.
