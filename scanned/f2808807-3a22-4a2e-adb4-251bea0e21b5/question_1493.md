# Q1493: receiveFromLRTConverter Supply Zero Transition Donation Accounting Merkle-free P1493

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to permanent freezing of funds? Probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the supply-zero transition path against receiveFromLRTConverter and look for donation accounting breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
