# Q340: depositETH Supply Zero Transition Deposit Limit Swell P0340

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: Swell swETH legacy route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the supply-zero transition path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Swell swETH legacy route; amount case available liquidity exactly; timing same block before updateRSETHPrice; caller model EOA caller.
