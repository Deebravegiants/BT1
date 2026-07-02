# Q578: depositAsset Buffer Under Reservation Oracle daily P0578

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: daily fee mint limit route; amount case 0.1 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case 0.1 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the buffer under-reservation path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: daily fee mint limit route; amount case 0.1 ether; timing same block after updateRSETHPrice; caller model EOA caller.
