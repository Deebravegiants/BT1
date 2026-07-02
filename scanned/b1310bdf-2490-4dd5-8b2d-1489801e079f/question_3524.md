# Q3524: updateRSETHPrice Fee On Transfer Token Skew Pause Race rsETH P3524

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case available liquidity exactly; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case available liquidity exactly; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the fee-on-transfer token skew path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: rsETH burn route; amount case available liquidity exactly; timing immediately after reward sendFunds; caller model EOA caller.
