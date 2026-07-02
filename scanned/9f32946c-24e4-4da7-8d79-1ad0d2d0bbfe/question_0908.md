# Q908: receiveFromRewardReceiver FirstExcludedIndex Boundary Price Update LRTConverter P0908

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the firstExcludedIndex boundary path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
