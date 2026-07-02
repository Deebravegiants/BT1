# Q3835: updateRSETHPrice Block Timestamp Boundary Pause Race withdrawal P3835

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: withdrawal request nonce route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the block-timestamp boundary path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: withdrawal request nonce route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.
