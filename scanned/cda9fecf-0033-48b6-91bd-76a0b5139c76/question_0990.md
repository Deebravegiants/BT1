# Q990: receiveFromRewardReceiver Claim Replay Reward Routing NodeDelegator P0990

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: NodeDelegator pod-share route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the claim replay path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: NodeDelegator pod-share route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
