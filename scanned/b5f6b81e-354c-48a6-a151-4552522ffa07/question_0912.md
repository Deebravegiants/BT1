# Q912: receiveFromRewardReceiver FirstExcludedIndex Boundary Price Update Aave P0912

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: Aave aWETH liquidity route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: attacker-created state followed by an honest operator action; probe condition: Aave aWETH liquidity route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the firstExcludedIndex boundary path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Aave aWETH liquidity route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
