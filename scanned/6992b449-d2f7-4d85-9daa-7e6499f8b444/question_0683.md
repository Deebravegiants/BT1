# Q683: depositAsset Allowance Race Reentrancy ETHx P0683

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: ETHx supported asset route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the allowance race path against depositAsset and look for reentrancy breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: ETHx supported asset route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller.
