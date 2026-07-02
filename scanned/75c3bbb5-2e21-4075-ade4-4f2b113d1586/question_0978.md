# Q978: receiveFromRewardReceiver Buffer Over Reservation Price Update daily P0978

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: daily fee mint limit route; amount case 0.1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: compare many dust calls against one large call; probe condition: daily fee mint limit route; amount case 0.1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the buffer over-reservation path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: daily fee mint limit route; amount case 0.1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
