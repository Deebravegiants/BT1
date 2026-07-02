# Q62: depositETH Fee On Transfer Token Skew Mint Rate stETH P0062

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: stETH supported asset route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the fee-on-transfer token skew path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: stETH supported asset route; amount case exact minAmount; timing same block before updateRSETHPrice; caller model EOA caller.
