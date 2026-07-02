# Q699: depositAsset Unbounded Event/data Growth Reentrancy Lido P0699

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: Lido stETH unstake route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the unbounded event/data growth path against depositAsset and look for reentrancy breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: Lido stETH unstake route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller.
