# Q1842: receiveFromNodeDelegator Cross Contract Stale Read Deposit Limit stETH P1842

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and make one contract read another contract before its state reflects a prior step in the same attack sequence, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: stETH supported asset route; amount case 32.000001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: make one contract read another contract before its state reflects a prior step in the same attack sequence; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case 32.000001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the cross-contract stale read path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: stETH supported asset route; amount case 32.000001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
