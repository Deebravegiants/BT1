# Q676: depositAsset Allowance Race Fee On Transfer queued P0676

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: queued buffer route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the allowance race path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: queued buffer route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
