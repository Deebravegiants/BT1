# Q1883: receiveFromNodeDelegator Supply Zero Transition Deposit Limit ETHx P1883

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: ETHx supported asset route; amount case daily limit exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case daily limit exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the supply-zero transition path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: ETHx supported asset route; amount case daily limit exactly; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
