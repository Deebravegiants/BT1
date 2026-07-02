# Q739: depositAsset Committed Assets Desync Oracle Lido P0739

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the committed-assets desync path against depositAsset and look for oracle breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller.
