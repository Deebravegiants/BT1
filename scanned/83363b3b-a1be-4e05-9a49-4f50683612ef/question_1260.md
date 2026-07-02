# Q1260: receiveFromLRTConverter Pause Boundary Race Withdrawal Liquidity Swell P1260

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to failure to deliver promised returns without principal loss? Probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: race a public action around a pause or public price-triggered pause transition; validation style: attacker-created state followed by an honest operator action; probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the pause boundary race path against receiveFromLRTConverter and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: Swell swETH legacy route; amount case minAmount minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
