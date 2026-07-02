# Q871: receiveFromRewardReceiver Pause Boundary Race Price Update EigenLayer P0871

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: EigenLayer queued-withdrawal route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: race a public action around a pause or public price-triggered pause transition; validation style: an attacker contract as msg.sender or recipient; probe condition: EigenLayer queued-withdrawal route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the pause boundary race path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: EigenLayer queued-withdrawal route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
