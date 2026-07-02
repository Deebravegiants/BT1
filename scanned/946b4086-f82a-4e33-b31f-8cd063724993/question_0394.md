# Q394: depositAsset Stale Price Sandwich Fee On Transfer deposit-limit P0394

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: deposit-limit accounting route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: deposit-limit accounting route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the stale-price sandwich path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: deposit-limit accounting route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
