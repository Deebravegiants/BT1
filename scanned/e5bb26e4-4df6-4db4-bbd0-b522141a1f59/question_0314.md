# Q314: depositETH Unbounded Event/data Growth Reentrancy deposit-limit P0314

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to protocol insolvency? Probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the unbounded event/data growth path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
