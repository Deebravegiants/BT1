# Q698: depositAsset Unbounded Event/data Growth Fee On Transfer daily P0698

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: daily fee mint limit route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the unbounded event/data growth path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: daily fee mint limit route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller.
