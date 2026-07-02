# Q563: depositAsset Fee Mint Limit Boundary Mint Rate ETHx P0563

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: ETHx supported asset route; amount case 0.1 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case 0.1 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the fee mint limit boundary path against depositAsset and look for mint rate breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: ETHx supported asset route; amount case 0.1 ether; timing same block after updateRSETHPrice; caller model EOA caller.
