# Q72: depositETH Fee On Transfer Token Skew Pause Race Aave P0072

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: Aave aWETH liquidity route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: attacker-created state followed by an honest operator action; probe condition: Aave aWETH liquidity route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the fee-on-transfer token skew path against depositETH and look for pause race breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: Aave aWETH liquidity route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller.
