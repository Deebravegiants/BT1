# Q179: depositETH Fee Mint Limit Boundary Mint Rate Lido P0179

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: Lido stETH unstake route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the fee mint limit boundary path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: Lido stETH unstake route; amount case 0.1 ether; timing same block before updateRSETHPrice; caller model EOA caller.
