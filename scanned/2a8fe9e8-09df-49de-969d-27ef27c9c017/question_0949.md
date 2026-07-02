# Q949: receiveFromRewardReceiver Aave Liquidity Shortfall Reward Routing LRTUnstakingVault P0949

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: LRTUnstakingVault instant-liquidity route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: one transaction using a contract wallet and controlled calldata; probe condition: LRTUnstakingVault instant-liquidity route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the Aave liquidity shortfall path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: LRTUnstakingVault instant-liquidity route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
