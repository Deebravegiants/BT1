# Q26: depositETH Round Up Insolvency Reentrancy LRTOracle P0026

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: LRTOracle price route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the round-up insolvency path against depositETH and look for reentrancy breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: LRTOracle price route; amount case 2 wei; timing same block before updateRSETHPrice; caller model EOA caller.
