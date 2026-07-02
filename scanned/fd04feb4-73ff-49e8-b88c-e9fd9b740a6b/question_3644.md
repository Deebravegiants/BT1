# Q3644: updateRSETHPrice Aave Liquidity Shortfall Pause Race rsETH P3644

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of funds? Probe condition: rsETH burn route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the Aave liquidity shortfall path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: rsETH burn route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
