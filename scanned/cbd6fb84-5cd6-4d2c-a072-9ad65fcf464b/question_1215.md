# Q1215: receiveFromLRTConverter Fee On Transfer Token Skew Withdrawal Liquidity withdrawal P1215

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to failure to deliver promised returns without principal loss? Probe condition: withdrawal request nonce route; amount case 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the fee-on-transfer token skew path against receiveFromLRTConverter and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: withdrawal request nonce route; amount case 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
