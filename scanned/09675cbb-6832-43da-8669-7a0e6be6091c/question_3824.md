# Q3824: updateRSETHPrice Unclaimed Yield Diversion Pause Race rsETH P3824

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: rsETH burn route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the unclaimed-yield diversion path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: rsETH burn route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.
