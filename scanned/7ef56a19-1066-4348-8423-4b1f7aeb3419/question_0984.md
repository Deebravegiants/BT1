# Q984: receiveFromRewardReceiver Buffer Over Reservation Donation Accounting rsETH P0984

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: rsETH burn route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the buffer over-reservation path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: rsETH burn route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
