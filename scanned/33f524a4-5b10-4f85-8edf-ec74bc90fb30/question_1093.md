# Q1093: receiveFromRewardReceiver Unexpected Receiver Revert Reward Routing Merkle-free P1093

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the unexpected receiver revert path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
