# Q3745: updateRSETHPrice Allowance Race Rounding rsETH P3745

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: rsETH transfer route; amount case 0.01 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 0.01 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use single transaction to exercise the allowance race path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH transfer route; amount case 0.01 ether; timing immediately after direct ETH donation; caller model EOA caller.
