# Q906: receiveFromRewardReceiver FirstExcludedIndex Boundary Donation Accounting LRTOracle P0906

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the firstExcludedIndex boundary path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: LRTOracle price route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
