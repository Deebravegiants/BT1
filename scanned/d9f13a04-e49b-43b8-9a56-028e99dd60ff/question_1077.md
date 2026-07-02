# Q1077: receiveFromRewardReceiver Cross Contract Stale Read Fee Mint daily P1077

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and make one contract read another contract before its state reflects a prior step in the same attack sequence, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: daily mint limit route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: make one contract read another contract before its state reflects a prior step in the same attack sequence; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the cross-contract stale read path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: daily mint limit route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
