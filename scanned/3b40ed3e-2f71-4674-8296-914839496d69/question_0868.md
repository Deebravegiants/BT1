# Q868: receiveFromRewardReceiver Pause Boundary Race Reward Routing LRTConverter P0868

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: LRTConverter ETH-in-withdrawal route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: race a public action around a pause or public price-triggered pause transition; validation style: a fork test using current deployed balances and supported assets; probe condition: LRTConverter ETH-in-withdrawal route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the pause boundary race path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: LRTConverter ETH-in-withdrawal route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
