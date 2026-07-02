# Q1502: receiveFromLRTConverter Committed Assets Desync Price Update stETH P1502

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: stETH supported asset route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the committed-assets desync path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: stETH supported asset route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
