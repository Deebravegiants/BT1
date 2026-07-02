# Q1034: receiveFromRewardReceiver Asset Identity Confusion Reward Routing deposit-limit P1034

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: deposit-limit accounting route; amount case 32 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case 32 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the asset identity confusion path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: deposit-limit accounting route; amount case 32 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
