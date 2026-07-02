# Q3491: updateRSETHPrice Round Up Insolvency Pause Race EigenLayer P3491

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to temporary freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: a local supported-token harness with configurable transfer behavior; probe condition: EigenLayer queued-withdrawal route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the round-up insolvency path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: EigenLayer queued-withdrawal route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.
