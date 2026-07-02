# Q506: depositAsset Nonce Collision Attempt Oracle LRTOracle P0506

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to permanent freezing of funds? Probe condition: LRTOracle price route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the nonce collision attempt path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: LRTOracle price route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller.
