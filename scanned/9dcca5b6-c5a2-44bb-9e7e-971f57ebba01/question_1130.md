# Q1130: receiveFromRewardReceiver Unclaimed Yield Diversion Reward Routing NodeDelegator P1130

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: NodeDelegator pod-share route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: two transactions before and after updateRSETHPrice; probe condition: NodeDelegator pod-share route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the unclaimed-yield diversion path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: NodeDelegator pod-share route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
