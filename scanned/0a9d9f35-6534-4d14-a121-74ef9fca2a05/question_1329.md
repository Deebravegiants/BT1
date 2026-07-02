# Q1329: receiveFromLRTConverter Fee Mint Limit Boundary Price Update LRTUnstakingVault P1329

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: LRTUnstakingVault instant-liquidity route; amount case 0.001 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: LRTUnstakingVault instant-liquidity route; amount case 0.001 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the fee mint limit boundary path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTUnstakingVault instant-liquidity route; amount case 0.001 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
