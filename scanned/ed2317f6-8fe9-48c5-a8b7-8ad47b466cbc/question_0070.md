# Q70: depositETH Fee On Transfer Token Skew Rounding NodeDelegator P0070

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: NodeDelegator pod-share route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: NodeDelegator pod-share route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the fee-on-transfer token skew path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: NodeDelegator pod-share route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller.
