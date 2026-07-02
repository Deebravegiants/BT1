# Q589: depositAsset Buffer Over Reservation Oracle LRTUnstakingVault P0589

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: LRTUnstakingVault instant-liquidity route; amount case 1 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: one transaction using a contract wallet and controlled calldata; probe condition: LRTUnstakingVault instant-liquidity route; amount case 1 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the buffer over-reservation path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: LRTUnstakingVault instant-liquidity route; amount case 1 ether; timing same block after updateRSETHPrice; caller model EOA caller.
