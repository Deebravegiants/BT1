# Q401: depositAsset Round Down Accumulation Oracle ETH P0401

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: ETH sentinel route; amount case 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the round-down accumulation path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: ETH sentinel route; amount case 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
