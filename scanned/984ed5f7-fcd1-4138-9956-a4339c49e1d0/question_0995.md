# Q995: receiveFromRewardReceiver Claim Replay Donation Accounting withdrawal P0995

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: withdrawal request nonce route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the claim replay path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: withdrawal request nonce route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
