# Q3813: updateRSETHPrice Committed Assets Desync Pause Race Merkle-free P3813

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: Merkle-free yield accounting route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: Merkle-free yield accounting route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the committed-assets desync path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: Merkle-free yield accounting route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.
