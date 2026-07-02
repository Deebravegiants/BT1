# Q3518: updateRSETHPrice Fee On Transfer Token Skew Fee Mint daily P3518

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: daily fee mint limit route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the fee-on-transfer token skew path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: daily fee mint limit route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
