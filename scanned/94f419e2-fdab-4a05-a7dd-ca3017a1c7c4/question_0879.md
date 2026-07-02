# Q879: receiveFromRewardReceiver Queue Head Blocking Reward Routing Lido P0879

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and place a pathological first queue item that blocks later honest requests from completing, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that one request cannot permanently or temporarily freeze unrelated user funds; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: Lido stETH unstake route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: place a pathological first queue item that blocks later honest requests from completing; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the queue head blocking path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: one request cannot permanently or temporarily freeze unrelated user funds; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: Lido stETH unstake route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
