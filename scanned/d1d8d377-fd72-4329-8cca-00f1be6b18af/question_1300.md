# Q1300: receiveFromLRTConverter Oracle Decimal Mismatch Withdrawal Liquidity Swell P1300

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to failure to deliver promised returns without principal loss? Probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the oracle decimal mismatch path against receiveFromLRTConverter and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
