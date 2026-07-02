# Q1123: receiveFromRewardReceiver Committed Assets Desync Reward Routing ETHx P1123

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: ETHx supported asset route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: an attacker contract as msg.sender or recipient; probe condition: ETHx supported asset route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the committed-assets desync path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: ETHx supported asset route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
