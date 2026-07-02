# Q450: depositAsset Fee On Transfer Token Skew Reentrancy NodeDelegator P0450

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: NodeDelegator pod-share route; amount case minAmount minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case minAmount minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the fee-on-transfer token skew path against depositAsset and look for reentrancy breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: NodeDelegator pod-share route; amount case minAmount minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
