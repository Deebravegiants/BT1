# Q1175: receiveFromLRTConverter Round Down Accumulation Withdrawal Liquidity withdrawal P1175

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to failure to deliver promised returns without principal loss? Probe condition: withdrawal request nonce route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the round-down accumulation path against receiveFromLRTConverter and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: withdrawal request nonce route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
