# Q392: depositAsset Stale Price Sandwich Deposit Limit Aave P0392

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: Aave aWETH liquidity route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Aave aWETH liquidity route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the stale-price sandwich path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Aave aWETH liquidity route; amount case deposit limit plus 1 wei; timing same block before updateRSETHPrice; caller model EOA caller.
