# Q1768: receiveFromNodeDelegator Failed External Call Ordering Deposit Limit LRTConverter P1768

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 0.1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: a fork test using current deployed balances and supported assets; probe condition: LRTConverter ETH-in-withdrawal route; amount case 0.1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the failed external call ordering path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 0.1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
