# Q759: depositAsset Block Timestamp Boundary Fee On Transfer Lido P0759

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: Lido stETH unstake route; amount case available liquidity plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case available liquidity plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the block-timestamp boundary path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: Lido stETH unstake route; amount case available liquidity plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
