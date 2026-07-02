# Q1765: receiveFromNodeDelegator Failed External Call Ordering Withdrawal Liquidity rsETH P1765

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and force an external transfer/withdraw/deposit call to fail after local accounting mutates, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH transfer route; amount case 0.1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: force an external transfer/withdraw/deposit call to fail after local accounting mutates; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 0.1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the failed external call ordering path against receiveFromNodeDelegator and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: failed integrations cannot leave burned rsETH, wrong counters, or inaccessible funds; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: rsETH transfer route; amount case 0.1 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
