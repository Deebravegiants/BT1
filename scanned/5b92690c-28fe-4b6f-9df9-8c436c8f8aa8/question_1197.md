# Q1197: receiveFromLRTConverter Zero Or Dust Edge Withdrawal Liquidity daily P1197

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to failure to deliver promised returns without principal loss? Probe condition: daily mint limit route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the zero-or-dust edge path against receiveFromLRTConverter and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: daily mint limit route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
