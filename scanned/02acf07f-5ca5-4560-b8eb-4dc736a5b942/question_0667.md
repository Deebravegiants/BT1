# Q667: depositAsset Min Amount Bypass Oracle FeeReceiver P0667

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: FeeReceiver reward route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the min-amount bypass path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: FeeReceiver reward route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
