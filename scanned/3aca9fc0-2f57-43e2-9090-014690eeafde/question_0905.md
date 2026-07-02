# Q905: receiveFromRewardReceiver FirstExcludedIndex Boundary Reward Routing rsETH P0905

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH transfer route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: several attacker accounts creating adjacent requests; probe condition: rsETH transfer route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the firstExcludedIndex boundary path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: rsETH transfer route; amount case 1 gwei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
