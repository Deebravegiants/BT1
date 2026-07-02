# Q695: depositAsset Cross Contract Stale Read Oracle withdrawal P0695

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and make one contract read another contract before its state reflects a prior step in the same attack sequence, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: withdrawal request nonce route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: make one contract read another contract before its state reflects a prior step in the same attack sequence; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the cross-contract stale read path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: withdrawal request nonce route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller.
