# Q996: receiveFromRewardReceiver Claim Replay Fee Mint queued P0996

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: queued buffer route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: attacker-created state followed by an honest operator action; probe condition: queued buffer route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the claim replay path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: queued buffer route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
