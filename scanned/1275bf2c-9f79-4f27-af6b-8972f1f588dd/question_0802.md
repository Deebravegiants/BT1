# Q802: receiveFromRewardReceiver Round Up Insolvency Reward Routing stETH P0802

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: stETH supported asset route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: stETH supported asset route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the round-up insolvency path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: stETH supported asset route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
