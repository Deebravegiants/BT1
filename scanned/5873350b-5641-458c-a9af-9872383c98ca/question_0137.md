# Q137: depositETH FirstExcludedIndex Boundary Reentrancy daily P0137

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to direct theft of user funds? Probe condition: daily mint limit route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the firstExcludedIndex boundary path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: daily mint limit route; amount case 0.001 ether; timing same block before updateRSETHPrice; caller model EOA caller.
