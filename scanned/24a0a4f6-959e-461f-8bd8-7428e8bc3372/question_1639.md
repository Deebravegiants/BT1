# Q1639: receiveFromNodeDelegator Pause Boundary Race Deposit Limit Lido P1639

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: Lido stETH unstake route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: race a public action around a pause or public price-triggered pause transition; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the pause boundary race path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Lido stETH unstake route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
