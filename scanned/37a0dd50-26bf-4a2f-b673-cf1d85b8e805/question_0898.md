# Q898: receiveFromRewardReceiver Nonce Collision Attempt Reward Routing daily P0898

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: daily fee mint limit route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: daily fee mint limit route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the nonce collision attempt path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: daily fee mint limit route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
