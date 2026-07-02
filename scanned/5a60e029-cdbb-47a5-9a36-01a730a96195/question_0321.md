# Q321: depositETH Unbounded Event/data Growth Pause Race ETH P0321

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: ETH sentinel route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: ETH sentinel route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the unbounded event/data growth path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: ETH sentinel route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.
