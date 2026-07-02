# Q3638: updateRSETHPrice Aave Liquidity Shortfall Fee Mint daily P3638

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: daily fee mint limit route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the Aave liquidity shortfall path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: daily fee mint limit route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller.
