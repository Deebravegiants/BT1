# Q313: depositETH Unbounded Event/data Growth Rounding Merkle-free P0313

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: Merkle-free yield accounting route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the unbounded event/data growth path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Merkle-free yield accounting route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
