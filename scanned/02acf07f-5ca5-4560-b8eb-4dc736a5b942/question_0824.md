# Q824: receiveFromRewardReceiver Direct ETH Donation Skew Reward Routing rsETH P0824

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH burn route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the direct ETH donation skew path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: rsETH burn route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
