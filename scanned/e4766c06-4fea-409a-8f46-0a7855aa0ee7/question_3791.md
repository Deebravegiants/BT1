# Q3791: updateRSETHPrice Unexpected Receiver Revert Pause Race EigenLayer P3791

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: EigenLayer queued-withdrawal route; amount case 1 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: a local supported-token harness with configurable transfer behavior; probe condition: EigenLayer queued-withdrawal route; amount case 1 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the unexpected receiver revert path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: EigenLayer queued-withdrawal route; amount case 1 ether; timing immediately after direct ETH donation; caller model EOA caller.
