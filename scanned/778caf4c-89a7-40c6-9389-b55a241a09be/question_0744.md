# Q744: depositAsset Committed Assets Desync Reentrancy rsETH P0744

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: rsETH burn route; amount case available liquidity plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case available liquidity plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the committed-assets desync path against depositAsset and look for reentrancy breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: rsETH burn route; amount case available liquidity plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
