# Q554: depositAsset Fee Mint Limit Boundary Fee On Transfer deposit-limit P0554

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: deposit-limit accounting route; amount case 0.01 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case 0.01 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the fee mint limit boundary path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: deposit-limit accounting route; amount case 0.01 ether; timing same block after updateRSETHPrice; caller model EOA caller.
