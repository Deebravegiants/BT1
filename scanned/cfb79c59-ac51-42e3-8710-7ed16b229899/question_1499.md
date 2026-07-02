# Q1499: receiveFromLRTConverter Supply Zero Transition Price Update Lido P1499

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: Lido stETH unstake route; amount case daily limit exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case daily limit exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the supply-zero transition path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Lido stETH unstake route; amount case daily limit exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
