# Q1149: receiveFromRewardReceiver Block Timestamp Boundary Reward Routing LRTUnstakingVault P1149

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: LRTUnstakingVault instant-liquidity route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: LRTUnstakingVault instant-liquidity route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the block-timestamp boundary path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: LRTUnstakingVault instant-liquidity route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
