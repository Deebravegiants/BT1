# Q1565: receiveFromNodeDelegator Round Up Insolvency Deposit Limit rsETH P1565

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: rsETH transfer route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: several attacker accounts creating adjacent requests; probe condition: rsETH transfer route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the round-up insolvency path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: rsETH transfer route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
