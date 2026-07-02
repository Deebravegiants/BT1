# Q291: depositETH Allowance Race Rounding EigenLayer P0291

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to permanent freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case daily limit exactly; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: a helper contract batching allowed public calls; probe condition: EigenLayer queued-withdrawal route; amount case daily limit exactly; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the allowance race path against depositETH and look for rounding breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: EigenLayer queued-withdrawal route; amount case daily limit exactly; timing same block before updateRSETHPrice; caller model EOA caller.
