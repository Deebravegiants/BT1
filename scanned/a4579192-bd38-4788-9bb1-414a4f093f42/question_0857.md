# Q857: receiveFromRewardReceiver Reentrant Token Callback Reward Routing daily P0857

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: daily mint limit route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the reentrant token callback path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: daily mint limit route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
