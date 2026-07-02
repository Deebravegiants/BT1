# Q1702: receiveFromNodeDelegator Highest Price Ratchet Deposit Limit stETH P1702

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: stETH supported asset route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: stETH supported asset route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the highest-price ratchet path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: stETH supported asset route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
