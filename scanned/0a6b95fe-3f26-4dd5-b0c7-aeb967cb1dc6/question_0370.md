# Q370: depositETH Unclaimed Yield Diversion Reentrancy NodeDelegator P0370

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: NodeDelegator pod-share route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: NodeDelegator pod-share route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the unclaimed-yield diversion path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: NodeDelegator pod-share route; amount case deposit limit minus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
