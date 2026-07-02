# Q289: depositETH Allowance Race Mint Rate LRTUnstakingVault P0289

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to failure to deliver promised returns without principal loss? Probe condition: LRTUnstakingVault instant-liquidity route; amount case daily limit exactly; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: one transaction using a contract wallet and controlled calldata; probe condition: LRTUnstakingVault instant-liquidity route; amount case daily limit exactly; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the allowance race path against depositETH and look for mint rate breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, mint rate must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: write a Foundry invariant that deposits then compares minted rsETH to normalized asset value and totalSupply backing. Use probe condition: LRTUnstakingVault instant-liquidity route; amount case daily limit exactly; timing same block before updateRSETHPrice; caller model EOA caller.
