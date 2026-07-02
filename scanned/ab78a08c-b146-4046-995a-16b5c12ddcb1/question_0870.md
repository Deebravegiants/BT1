# Q870: receiveFromRewardReceiver Pause Boundary Race Fee Mint NodeDelegator P0870

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: NodeDelegator pod-share route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: race a public action around a pause or public price-triggered pause transition; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the pause boundary race path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: NodeDelegator pod-share route; amount case exact minAmount; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
