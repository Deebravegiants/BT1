# Q1849: receiveFromNodeDelegator Unbounded Event/data Growth Deposit Limit LRTUnstakingVault P1849

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: LRTUnstakingVault instant-liquidity route; amount case 32.000001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: one transaction using a contract wallet and controlled calldata; probe condition: LRTUnstakingVault instant-liquidity route; amount case 32.000001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the unbounded event/data growth path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: LRTUnstakingVault instant-liquidity route; amount case 32.000001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
