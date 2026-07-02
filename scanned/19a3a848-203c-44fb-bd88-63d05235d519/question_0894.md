# Q894: receiveFromRewardReceiver Nonce Collision Attempt Reward Routing deposit-limit P0894

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: deposit-limit accounting route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the nonce collision attempt path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: deposit-limit accounting route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
