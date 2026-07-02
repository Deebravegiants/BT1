# Q316: depositETH Unbounded Event/data Growth Fee Mint queued P0316

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: queued buffer route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the unbounded event/data growth path against depositETH and look for fee mint breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: queued buffer route; amount case available liquidity minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
