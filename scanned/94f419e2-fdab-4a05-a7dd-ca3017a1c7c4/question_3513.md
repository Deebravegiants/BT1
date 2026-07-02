# Q3513: updateRSETHPrice Direct ETH Donation Skew Pause Race Merkle-free P3513

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to temporary freezing of funds? Probe condition: Merkle-free yield accounting route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: Merkle-free yield accounting route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the direct ETH donation skew path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: Merkle-free yield accounting route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
