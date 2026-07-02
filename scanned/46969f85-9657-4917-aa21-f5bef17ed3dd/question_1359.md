# Q1359: receiveFromLRTConverter Buffer Over Reservation Withdrawal Liquidity Lido P1359

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to failure to deliver promised returns without principal loss? Probe condition: Lido stETH unstake route; amount case 0.01 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case 0.01 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the buffer over-reservation path against receiveFromLRTConverter and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: Lido stETH unstake route; amount case 0.01 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
